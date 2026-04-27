# Amazon Quick Setup (Prerequisite)

Amazon Quick must be subscribed and configured BEFORE deploying the CloudFormation stack.

## 1. Subscribe to Amazon Quick

1. Go to the AWS Console → Amazon QuickSight
2. Select Enterprise or Standard plan
3. Configure the account in the us-east-1 region

## 2. Get the user ARN

```bash
aws quicksight list-users --aws-account-id ACCOUNT_ID --namespace default --region us-east-1
```

The ARN will have the format: `arn:aws:quicksight:us-east-1:ACCOUNT_ID:user/default/USERNAME`

This ARN is passed as the `QuickSightUserArn` parameter when deploying the stack.

## 3. Configure Amazon Quick permissions for S3 and Athena

From the Amazon Quick console:
1. Manage → Security & permissions
2. Under "Amazon Quick access to AWS services", enable:
   - Amazon Athena
   - Amazon S3
3. Select the project buckets:
   - `data-processing-raw-data-*`
   - `data-processing-athena-results-*`

## 4. Resources automatically created by the stack

The CloudFormation template automatically creates:
- DataSource connected to Athena
- DataSet pointing to the `processed_data` table
- 2 Analyses (General Summary and Detail & Trends)
- 2 Published Dashboards
- IAM Policy with permissions for Athena, Glue Catalog, and S3

## 5. Post-deployment verification

```bash
# Verify the DataSource was created correctly
aws quicksight describe-data-source \
  --aws-account-id ACCOUNT_ID \
  --data-source-id data-processing-athena-ds \
  --region us-east-1

# Verify the dashboards
aws quicksight list-dashboards --aws-account-id ACCOUNT_ID --region us-east-1
```

## Notes

- Amazon Quick must be in the same region as Athena and Glue (us-east-1)
- Dashboards can be shared with other users from the Amazon Quick console
- SPICE is used as the import mode for better performance
- The Glue Job runs manually; dashboards update when the DataSet is refreshed
