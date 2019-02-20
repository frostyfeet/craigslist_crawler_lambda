data "template_file" "iam_assume_role_lambda" {
  template = "${file("policies/iam_assume_role.json")}"

  vars {
    aws_service = "lambda"
  }
}

data "template_file" "craigslist_lambda_policy" {
  template = "${file("./policies/craigslist_lambda.json")}"
}

resource "aws_cloudwatch_event_rule" "craigslist_lambda" {
  name        = "craigslist_events"
  description = "Cron for lambda"

  schedule_expression = "rate(120 minutes)" 
}

resource "aws_lambda_permission" "craigslist_lambda" {
  statement_id  = "craigslist-lambda-trigger"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.craigslist_lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.craigslist_lambda.arn}"
}

resource "aws_cloudwatch_event_target" "craigslist_to_lambda" {
  rule = "${aws_cloudwatch_event_rule.craigslist_lambda.name}"
  arn  = "${aws_lambda_function.craigslist_lambda.arn}"
}

resource "aws_lambda_function" "craigslist_lambda" {
  filename         = "./build/lambda.zip"
  function_name    = "craigslist_lambda"
  description      = "Updates the craigslists"
  runtime          = "python3.7"
  role             = "${aws_iam_role.craigslist_lambda_role.arn}"
  handler          = "craigslist.handler"
  source_code_hash = "${base64sha256(file("./build/lambda.zip"))}"
  memory_size      = 128 
  timeout          = 900

  tags {
    "Contact"     = "${var.contact}"
    "Service"     = "${var.service}"
    "Description" = "Managed via Terraform"
    "Environment" = "${var.env}"
  }
}

resource "aws_iam_role_policy_attachment" "craigslist_lambda_policy_att" {
  role       = "${aws_iam_role.craigslist_lambda_role.name}"
  policy_arn = "${aws_iam_policy.craigslist_lambda_policy.arn}"
}

resource "aws_iam_role_policy_attachment" "craigslist_lambda_policy_att_basic" {
  role       = "${aws_iam_role.craigslist_lambda_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "craigslist_lambda_policy" {
  name        = "craigslist_lambda_policy"
  description = "Grants access to describe instances"
  policy      = "${data.template_file.craigslist_lambda_policy.rendered}"
}

resource "aws_iam_role" "craigslist_lambda_role" {
  name               = "craigslist_lambda_role"
  assume_role_policy = "${data.template_file.iam_assume_role_lambda.rendered}"
}
