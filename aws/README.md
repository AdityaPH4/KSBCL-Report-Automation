# Hosting the 4 crawlers on AWS (ECS Fargate + EventBridge Scheduler)

Status: container image built and verified end-to-end (real KSBCL login, real
data, real write to `robinhood.d88_cider_sales`) on native ARM64 Docker.
Nothing is deployed to AWS yet.

Why this split: `toit-cli-user` (the AWS CLI credential available in this
session) can read ECR/EC2/RDS and push images, but is explicitly denied ECS,
EventBridge Scheduler, IAM, CloudWatch Logs, and EC2 security-group writes.
Everything in **Part 1** needs your own AWS access (Console, or a more
privileged CLI profile). Once those exist, Claude can do **Part 2** with the
current session's credentials.

All resource names/ARNs below assume account `746669213597`, region
`ap-south-1`, VPC `vpc-065647136e489b75f` (the same VPC the RDS instance is
in). Adjust if you deploy elsewhere.

---

## Part 1 — steps that need your own AWS access

### 1. Create the ECR repository
```bash
aws ecr create-repository --repository-name robinhood-crawlers --region ap-south-1
```

### 2. Create the secret (run this yourself — it reads your own .env directly, nothing passes through Claude)
```bash
cd /Users/headoffice/RobinHood
aws secretsmanager create-secret --name robinhood/crawler-env --secret-string "$(.venv/bin/python3 -c "
from dotenv import load_dotenv
import os, json
load_dotenv()
print(json.dumps({
    'KSBCL_USERNAME': os.environ['KSBCL_USERNAME'],
    'KSBCL_PASSWORD': os.environ['KSBCL_PASSWORD'],
    'KSBCL_CIDER_USERNAME': os.environ['KSBCL_CIDER_USERNAME'],
    'KSBCL_CIDER_PASSWORD': os.environ['KSBCL_CIDER_PASSWORD'],
    'DATABASE_URL': os.environ['DATABASE_URL'],
}))
")"
```

### 3. Create the ECS task execution role
```bash
aws iam create-role \
  --role-name robinhoodCrawlerExecutionRole \
  --assume-role-policy-document file://aws/execution-role-trust-policy.json

aws iam attach-role-policy \
  --role-name robinhoodCrawlerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam put-role-policy \
  --role-name robinhoodCrawlerExecutionRole \
  --policy-name robinhoodCrawlerSecretsAccess \
  --policy-document file://aws/execution-role-secrets-policy.json
```

### 4. Create the EventBridge Scheduler role
```bash
aws iam create-role \
  --role-name robinhoodSchedulerRole \
  --assume-role-policy-document file://aws/scheduler-trust-policy.json

aws iam put-role-policy \
  --role-name robinhoodSchedulerRole \
  --policy-name robinhoodSchedulerRunTask \
  --policy-document file://aws/scheduler-run-task-policy.json
```

### 5. Create a security group for the crawler tasks + allow it into the RDS SG
This mirrors the existing pattern already on the RDS security group
(`sg-0ef43d20c18b3507b`) — the "EC2 backend server (VPC internal)" rule is a
security-group reference, not a raw IP. Do the same for the crawlers instead
of IP-allowlisting (which breaks every time Fargate assigns a new IP):
```bash
aws ec2 create-security-group \
  --group-name robinhood-crawler-sg \
  --description "RobinHood ECS Fargate crawler tasks" \
  --vpc-id vpc-065647136e489b75f
# note the returned GroupId as $CRAWLER_SG below

aws ec2 authorize-security-group-ingress \
  --group-id sg-0ef43d20c18b3507b \
  --protocol tcp --port 5432 \
  --source-group $CRAWLER_SG \
  --description "RobinHood ECS Fargate crawlers (VPC internal)"
```

### 6. Create the ECS cluster
```bash
aws ecs create-cluster --cluster-name robinhood
```

---

## Part 2 — once the above exists, tell Claude and it will

1. Push the built image to ECR:
   ```bash
   aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 746669213597.dkr.ecr.ap-south-1.amazonaws.com
   docker tag robinhood-crawlers:arm64 746669213597.dkr.ecr.ap-south-1.amazonaws.com/robinhood-crawlers:latest
   docker push 746669213597.dkr.ecr.ap-south-1.amazonaws.com/robinhood-crawlers:latest
   ```
2. Register the task definition: `aws ecs register-task-definition --cli-input-json file://aws/task-definition.json`
3. Create 4 EventBridge Scheduler schedules (one per crawler), each targeting
   `ecs:RunTask` on the `robinhood` cluster with a `containerOverrides.command`
   picking the right script (`run_daily_d88_bottles.py`,
   `run_daily_d88_cider.py`, `run_daily_d94_bottles.py`,
   `run_daily_d94_cider.py`), staggered 10 minutes apart, daily in IST.
4. Verify: wait for the first scheduled run (or trigger one manually with
   `aws scheduler invoke` / a manual `ecs run-task`) and check
   `robinhood.*` tables for a new `import_id`, plus CloudWatch Logs
   (`/ecs/robinhood-crawler`) for the run output.

Needs the subnet IDs too (already public, any of the three work):
`subnet-06ce0c59d585beb7c`, `subnet-0721f15f5e4019112`, `subnet-01c71ee518661bff2`.
