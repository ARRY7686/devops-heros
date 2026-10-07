# Session 18 Homework: Terraform and Infrastructure as Code

All exercises in `session18-terraform-iac/` (01 to 09, plus `terraform-s3-demo`) were run with **Terraform 1.16.5** and **hashicorp/aws 6.x** from a Windows PowerShell terminal.

**AWS target: a local AWS emulator instead of a real account.** No AWS credentials are configured on this machine, so every `terraform apply` and `destroy` ran against **[Moto](https://github.com/getmoto/moto)** (`motoserver/moto`), an open-source AWS emulator, in Docker on `localhost:4566`. LocalStack was the first choice, but its current image requires a paid auth token, and the free 4.4 image does not implement the S3 Control tagging API that AWS provider 6.x calls. LocalStack is built on Moto, so running Moto directly is the same idea. The `.tf` files are unchanged. Only environment variables redirect the provider:

```text
AWS_ACCESS_KEY_ID=test  AWS_SECRET_ACCESS_KEY=test  AWS_REGION=ap-south-1
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ENDPOINT_URL_S3=http://s3.localhost.localstack.cloud:4566          # virtual-host bucket names resolve to 127.0.0.1
AWS_ENDPOINT_URL_S3_CONTROL=http://localhost.localstack.cloud:4566
```

The same `.tf` files work against real AWS by removing those variables and running `aws configure`.

Notes:
- `terraform apply` was run with `-auto-approve` so that each screenshot shows a complete run; the plan shown is the one you would confirm with `yes`.
- `terraform fmt` was run as `fmt -check` so the course files were not rewritten.
- Exercises that edit `.tf` files were done in copies under `homework/`.

Each command and its output is captured in a terminal screenshot under [`screenshots/`](screenshots/), and the plain-text transcript of every step is in [`outputs/`](outputs/).

## Contents

- [Setup](#setup)
- [01 IaC basics](#01-iac-basics)
- [02 Terraform architecture](#02-terraform-architecture)
- [03 Providers](#03-providers)
- [04 Resources](#04-resources)
- [05 Variables](#05-variables)
- [06 Outputs](#06-outputs)
- [07 Init, plan, apply](#07-init-plan-apply)
- [08 Destroy](#08-destroy)
- [09 State](#09-state)
- [terraform-s3-demo](#terraform-s3-demo)
- [Cleanup](#cleanup)
- [Key learnings](#key-learnings)

## Setup

```powershell
terraform version
aws sts get-caller-identity      # account 123456789012 (Moto)
aws s3 ls
```

**00-setup/01-tools**

![00-setup/01-tools](screenshots/00-setup/01-tools.png)


## 01 IaC basics

`init → fmt -check → validate → plan → apply → output → state list → destroy` on an S3 bucket created with `bucket_prefix = "session18-iac-"`.

- `Plan: 1 to add`, then `Apply complete! Resources: 1 added`.
- `bucket_name = "session18-iac-…"`, and `aws s3 ls` shows the bucket.
- `Destroy complete! Resources: 1 destroyed`, and `aws s3 ls` is empty again.

**01-iac-basics/01-init-validate-plan-part1**

![01-iac-basics/01-init-validate-plan-part1](screenshots/01-iac-basics/01-init-validate-plan-part1.png)

**01-iac-basics/01-init-validate-plan-part2**

![01-iac-basics/01-init-validate-plan-part2](screenshots/01-iac-basics/01-init-validate-plan-part2.png)

**01-iac-basics/01-init-validate-plan-part3**

![01-iac-basics/01-init-validate-plan-part3](screenshots/01-iac-basics/01-init-validate-plan-part3.png)

**01-iac-basics/02-apply-verify-destroy-part1**

![01-iac-basics/02-apply-verify-destroy-part1](screenshots/01-iac-basics/02-apply-verify-destroy-part1.png)

**01-iac-basics/02-apply-verify-destroy-part2**

![01-iac-basics/02-apply-verify-destroy-part2](screenshots/01-iac-basics/02-apply-verify-destroy-part2.png)

**01-iac-basics/02-apply-verify-destroy-part3**

![01-iac-basics/02-apply-verify-destroy-part3](screenshots/01-iac-basics/02-apply-verify-destroy-part3.png)


## 02 Terraform architecture

Configuration → CLI → provider plugin → AWS API → state file. `terraform show` prints the stored state of `aws_s3_bucket.architecture_demo` (ARN, region, tags). After `destroy`, the directory still holds `.terraform/` (the provider), `.terraform.lock.hcl`, and `terraform.tfstate` plus `.backup` (now with no resources).

**02-terraform-architecture/01-run-part1**

![02-terraform-architecture/01-run-part1](screenshots/02-terraform-architecture/01-run-part1.png)

**02-terraform-architecture/01-run-part2**

![02-terraform-architecture/01-run-part2](screenshots/02-terraform-architecture/01-run-part2.png)

**02-terraform-architecture/01-run-part3**

![02-terraform-architecture/01-run-part3](screenshots/02-terraform-architecture/01-run-part3.png)

**02-terraform-architecture/02-destroy-part1**

![02-terraform-architecture/02-destroy-part1](screenshots/02-terraform-architecture/02-destroy-part1.png)

**02-terraform-architecture/02-destroy-part2**

![02-terraform-architecture/02-destroy-part2](screenshots/02-terraform-architecture/02-destroy-part2.png)


## 03 Providers

- `terraform init` downloads `hashicorp/aws` (constraint `~> 6.0`) and pins it in `.terraform.lock.hcl`.
- `terraform providers` shows the provider tree.
- `terraform plan -var aws_region=us-east-1` shows the provider region is a variable.
- `aws sts get-caller-identity` is the authentication check the README asks for.

**03-providers/01-provider-part1**

![03-providers/01-provider-part1](screenshots/03-providers/01-provider-part1.png)

**03-providers/01-provider-part2**

![03-providers/01-provider-part2](screenshots/03-providers/01-provider-part2.png)

**03-providers/02-apply-destroy-part1**

![03-providers/02-apply-destroy-part1](screenshots/03-providers/02-apply-destroy-part1.png)

**03-providers/02-apply-destroy-part2**

![03-providers/02-apply-destroy-part2](screenshots/03-providers/02-apply-destroy-part2.png)

**03-providers/02-apply-destroy-part3**

![03-providers/02-apply-destroy-part3](screenshots/03-providers/02-apply-destroy-part3.png)


## 04 Resources

`aws_s3_bucket.demo` was created, then listed with `state list`, inspected with `show` (ARN, `bucket_regional_domain_name`, tags `Environment=dev`), and destroyed.

**04-resources/01-resource-part1**

![04-resources/01-resource-part1](screenshots/04-resources/01-resource-part1.png)

**04-resources/01-resource-part2**

![04-resources/01-resource-part2](screenshots/04-resources/01-resource-part2.png)

**04-resources/01-resource-part3**

![04-resources/01-resource-part3](screenshots/04-resources/01-resource-part3.png)

**04-resources/01-resource-part4**

![04-resources/01-resource-part4](screenshots/04-resources/01-resource-part4.png)


## 05 Variables

| Values used | Resulting bucket prefix / tags |
| :--- | :--- |
| Defaults | `terraform-training-dev-`, Project `terraform-training`, Environment `dev` |
| `terraform.tfvars` (copied from `terraform.tfvars.example`) | `student-project-dev-` |
| `-var environment=test` (the exercise) | `student-project-test-`, Environment `test` |

Precedence: `-var` > `*.tfvars` > `default`. The copied `terraform.tfvars` was deleted again; it is git-ignored on purpose.

**05-variables/01-defaults-part1**

![05-variables/01-defaults-part1](screenshots/05-variables/01-defaults-part1.png)

**05-variables/01-defaults-part2**

![05-variables/01-defaults-part2](screenshots/05-variables/01-defaults-part2.png)

**05-variables/02-tfvars-and-overrides**

![05-variables/02-tfvars-and-overrides](screenshots/05-variables/02-tfvars-and-overrides.png)


## 06 Outputs

- `terraform output` lists `bucket_id`, `bucket_arn` and `bucket_region`. `terraform output bucket_id` prints a single value, and `-json` gives machine-readable output.
- **Exercise:** in a copy (`homework/06-outputs-exercise`), I added `output "bucket_name" { value = aws_s3_bucket.demo.bucket }`. After `apply`, `terraform output bucket_name` printed the bucket name.

**06-outputs/01-outputs-part1**

![06-outputs/01-outputs-part1](screenshots/06-outputs/01-outputs-part1.png)

**06-outputs/01-outputs-part2**

![06-outputs/01-outputs-part2](screenshots/06-outputs/01-outputs-part2.png)

**06-outputs/01-outputs-part3**

![06-outputs/01-outputs-part3](screenshots/06-outputs/01-outputs-part3.png)

**06-outputs/01-outputs-part4**

![06-outputs/01-outputs-part4](screenshots/06-outputs/01-outputs-part4.png)

**06-outputs/02-exercise-bucket-name-output-part1**

![06-outputs/02-exercise-bucket-name-output-part1](screenshots/06-outputs/02-exercise-bucket-name-output-part1.png)

**06-outputs/02-exercise-bucket-name-output-part2**

![06-outputs/02-exercise-bucket-name-output-part2](screenshots/06-outputs/02-exercise-bucket-name-output-part2.png)

**06-outputs/02-exercise-bucket-name-output-part3**

![06-outputs/02-exercise-bucket-name-output-part3](screenshots/06-outputs/02-exercise-bucket-name-output-part3.png)


## 07 Init, plan, apply

Saved-plan workflow:

```powershell
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan     # applies exactly the reviewed plan, no prompt
```

**07-init-plan-apply/01-saved-plan-part1**

![07-init-plan-apply/01-saved-plan-part1](screenshots/07-init-plan-apply/01-saved-plan-part1.png)

**07-init-plan-apply/01-saved-plan-part2**

![07-init-plan-apply/01-saved-plan-part2](screenshots/07-init-plan-apply/01-saved-plan-part2.png)

**07-init-plan-apply/01-saved-plan-part3**

![07-init-plan-apply/01-saved-plan-part3](screenshots/07-init-plan-apply/01-saved-plan-part3.png)

**07-init-plan-apply/02-destroy**

![07-init-plan-apply/02-destroy](screenshots/07-init-plan-apply/02-destroy.png)


## 08 Destroy

`terraform plan -destroy` previews `Plan: 0 to add, 0 to change, 1 to destroy`. After `destroy`, `state list` is empty and `aws s3 ls` shows nothing.

**08-destroy/01-destroy-part1**

![08-destroy/01-destroy-part1](screenshots/08-destroy/01-destroy-part1.png)

**08-destroy/01-destroy-part2**

![08-destroy/01-destroy-part2](screenshots/08-destroy/01-destroy-part2.png)

**08-destroy/01-destroy-part3**

![08-destroy/01-destroy-part3](screenshots/08-destroy/01-destroy-part3.png)

**08-destroy/01-destroy-part4**

![08-destroy/01-destroy-part4](screenshots/08-destroy/01-destroy-part4.png)


## 09 State

- `state list` → `aws_s3_bucket.state_demo`.
- `state show aws_s3_bucket.state_demo` shows the full attributes.
- `state pull` prints the raw JSON (`version`, `serial`, `lineage`, `resources`). It holds every attribute in plain text, so never commit state to Git; use a remote backend.
- **Exercise** (in the copy `homework/09-state-exercise`): changing the `Name` tag gives `# aws_s3_bucket.state_demo will be updated in-place` and `Plan: 0 to add, 1 to change, 0 to destroy`, then `Apply complete! Resources: 0 added, 1 changed`. `state show` displays the new tag.

**09-state/01-inspect-part1**

![09-state/01-inspect-part1](screenshots/09-state/01-inspect-part1.png)

**09-state/01-inspect-part2**

![09-state/01-inspect-part2](screenshots/09-state/01-inspect-part2.png)

**09-state/01-inspect-part3**

![09-state/01-inspect-part3](screenshots/09-state/01-inspect-part3.png)

**09-state/02-state-pull-part1**

![09-state/02-state-pull-part1](screenshots/09-state/02-state-pull-part1.png)

**09-state/02-state-pull-part2**

![09-state/02-state-pull-part2](screenshots/09-state/02-state-pull-part2.png)

**09-state/02-state-pull-part3**

![09-state/02-state-pull-part3](screenshots/09-state/02-state-pull-part3.png)

**09-state/03-exercise-change-tag-part1**

![09-state/03-exercise-change-tag-part1](screenshots/09-state/03-exercise-change-tag-part1.png)

**09-state/03-exercise-change-tag-part2**

![09-state/03-exercise-change-tag-part2](screenshots/09-state/03-exercise-change-tag-part2.png)

**09-state/03-exercise-change-tag-part3**

![09-state/03-exercise-change-tag-part3](screenshots/09-state/03-exercise-change-tag-part3.png)

**09-state/04-cleanup-part1**

![09-state/04-cleanup-part1](screenshots/09-state/04-cleanup-part1.png)

**09-state/04-cleanup-part2**

![09-state/04-cleanup-part2](screenshots/09-state/04-cleanup-part2.png)


## terraform-s3-demo

A multi-file layout: `terraform.tf`, `providers.tf`, `variables.tf`, `main.tf`, `outputs.tf`.

- `terraform validate` on the course folder: **Success**. Its `outputs.tf` uses `type = string` inside `output` blocks, which Terraform 1.16 accepts.
- The copy in `homework/terraform-s3-demo-fixed` has the `type` lines removed so it also works on older Terraform versions, which reject that argument.
- Applied with `-var bucket_name=devops553-session18-demo`, because the default name `yatri1107` is someone else's globally unique bucket name. Then destroyed (`force_destroy = true`).
- `aws s3api get-bucket-tagging` returned `NoSuchTagSet`. AWS provider 6.x writes bucket tags through the S3 Control `TagResource` API, and Moto's S3 `GetBucketTagging` does not reflect those tags. This is an emulator gap: the tags (`ManagedBy=Terraform`, `Project=Session18`) are in the Terraform plan and state, and on real AWS `get-bucket-tagging` would return them.

**terraform-s3-demo/01-validate-error**

![terraform-s3-demo/01-validate-error](screenshots/terraform-s3-demo/01-validate-error.png)

**terraform-s3-demo/02-fix**

![terraform-s3-demo/02-fix](screenshots/terraform-s3-demo/02-fix.png)

**terraform-s3-demo/03-apply-destroy-part1**

![terraform-s3-demo/03-apply-destroy-part1](screenshots/terraform-s3-demo/03-apply-destroy-part1.png)

**terraform-s3-demo/03-apply-destroy-part2**

![terraform-s3-demo/03-apply-destroy-part2](screenshots/terraform-s3-demo/03-apply-destroy-part2.png)

**terraform-s3-demo/03-apply-destroy-part3**

![terraform-s3-demo/03-apply-destroy-part3](screenshots/terraform-s3-demo/03-apply-destroy-part3.png)


## Cleanup

All buckets were destroyed. The `.terraform/` folders, state files and generated lock files were deleted from the course folders. `terraform init` had added a hash line to the tracked `terraform-s3-demo/.terraform.lock.hcl`, so I restored that file with `git checkout`. `git status` shows only the new `homework/` folder.

**cleanup/01-cleanup**

![cleanup/01-cleanup](screenshots/cleanup/01-cleanup.png)


## Key learnings

- **IaC:** infrastructure is described in versioned code and reviewed with `plan` before anything changes.
- **Workflow:** `init` (providers) → `fmt`/`validate` (syntax) → `plan` (diff against state) → `apply` → `destroy`.
- **Variables and outputs** make one configuration reusable. Outputs expose values to people and to other tools.
- **State** maps code to real resource IDs. Inspect it with `state list/show/pull` and never edit it by hand.
- **Saved plans** (`-out`) make sure what was reviewed is exactly what gets applied.
