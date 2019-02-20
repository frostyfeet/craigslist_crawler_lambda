import abc
import boto3
import pickle
from slackclient import SlackClient


class SearchMaster(object):
    aws_region = "us-west-2"
    s3_bucket_name = "temp-lambda-files"
    temp_path = "/tmp/"
    client = boto3.client('s3', region_name=aws_region)

    def __init__(self, urls, s3_filename, slack_token):
        self.urls = urls
        self.s3_filename = s3_filename
        self.old_data = self.read_s3_file()
        self.slack_token = slack_token

    def read_s3_file(self):
        full_path = "{}{}".format(self.temp_path, self.s3_filename)
        try:
            self.client.download_file(self.s3_bucket_name, self.s3_filename, full_path)
            pickle_in = open(full_path, "rb")
            return pickle.load(pickle_in)
        except Exception as e:
            print("Returning empty list: {}".format(e))
            return {
                'Results': []
            }

    def write_s3_file(self):
        try:
            full_path = "{}{}".format(self.temp_path, self.s3_filename)
            pickle_out = open(full_path, "wb")
            pickle.dump(self.old_data, pickle_out)
            pickle_out.close()
            self.client.upload_file(full_path, self.s3_bucket_name, self.s3_filename)
            return True
        except Exception as e:
            print("Error uploading file: {}".format(e))
            return False

    def add_new_results(self, new_results):
        self.old_data['Results'] = self.old_data['Results'] + new_results

    def get_new_results(self, new_results):
        return [value for value in new_results if value not in self.old_data['Results']] 

    def send_slack(self, content):
        sc = SlackClient(self.slack_token)
        sc.api_call(
            "chat.postMessage",
            channel="#general",
            text=content,
            as_user=True,
            mrkdwn=True,
            username="CraigslistBot"
            )
    
    
