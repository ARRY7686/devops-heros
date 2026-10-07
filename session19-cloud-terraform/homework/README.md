# Session 19 Homework: Cloud Networking with Terraform

The theory topics (01–05) and the Terraform labs (06 VPC, 07 workflow, 08 mini project, plus its optional EC2 extension) were run with **Terraform 1.16.5** and **hashicorp/aws 6.x** from a Windows PowerShell terminal.

**AWS target:** as in Session 18, there are no AWS credentials on this machine, so everything was applied to the **Moto** AWS emulator in Docker (`localhost:4566`). Only environment variables point the provider and AWS CLI at it. The `.tf` files are unchanged and work on real AWS as they are. Moto implements VPCs, subnets, internet gateways, route tables, security groups and EC2 instances, so every resource below was really created and destroyed through the AWS API, and every `aws ec2 describe-*` command from the READMEs was run against it.

Each command and its output is captured in a terminal screenshot under [`screenshots/`](screenshots/), and the plain-text transcript of every step is in [`outputs/`](outputs/).

## Contents

- [01–05 Concepts](#0105-concepts)
- [06 Terraform VPC lab](#06-terraform-vpc-lab)
- [07 Terraform workflow](#07-terraform-workflow)
- [08 Mini project](#08-mini-project)
- [08 Optional extension: EC2](#08-optional-extension-ec2)
- [Cleanup](#cleanup)
- [Interview / practice answers](#interview--practice-answers)

**00-setup/01-tools**

![00-setup/01-tools](screenshots/00-setup/01-tools.png)


## 01–05 Concepts

| Topic | Summary |
| :--- | :--- |
| Service models | **IaaS**: you manage the OS and up (EC2, VPC). **PaaS**: you manage the app (Elastic Beanstalk, RDS). **SaaS**: you only use the software (Gmail). |
| Regions and AZs | A region (`ap-south-1`) is a geographic area; an AZ (`ap-south-1a/b/c`) is an isolated data centre group within it. Spreading across AZs survives the loss of one data centre. |
| VPC and subnets | A VPC is a private network (`10.0.0.0/16` = 65,536 addresses). Subnets are slices of it in a single AZ (`10.0.1.0/24` = 256 addresses, 251 usable on AWS). |
| Route table + IGW | A subnet is *public* only when its route table sends `0.0.0.0/0` to an Internet Gateway. Otherwise it's private. |
| Security groups | Stateful, instance-level firewalls with allow rules only. Return traffic is allowed automatically. |

```powershell
aws configure get region
aws sts get-caller-identity
aws ec2 describe-regions --query 'Regions[].RegionName' --output text
aws ec2 describe-availability-zones --output table
```

**02-regions-and-azs/01-region**

![02-regions-and-azs/01-region](screenshots/02-regions-and-azs/01-region.png)


## 06 Terraform VPC lab

Architecture: VPC `10.0.0.0/16` → public subnet `10.0.1.0/24` (`ap-south-1a`, public IP on launch) → Internet Gateway → route table with `0.0.0.0/0 → igw` → association → security group `session19-web-sg` allowing 80/443 in and all traffic out.

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init; terraform fmt -check; terraform validate
terraform plan                 # Plan: 6 to add
terraform apply -auto-approve  # Apply complete! Resources: 6 added
terraform state list
terraform output               # vpc_id, vpc_cidr, subnet_id, security_group_id
```

Verified with the AWS CLI commands from the README:
- The VPC is `available` with CIDR `10.0.0.0/16`.
- The subnet is in `ap-south-1a`.
- The route table has `10.0.0.0/16 → local` and `0.0.0.0/0 → igw-…`.
- The IGW is attached to the VPC.
- The security group allows tcp/80 and tcp/443.

`terraform plan -destroy` and `terraform destroy` removed all 6 resources.

**06-terraform-vpc/01-init-validate**

![06-terraform-vpc/01-init-validate](screenshots/06-terraform-vpc/01-init-validate.png)

**06-terraform-vpc/02-plan-part1**

![06-terraform-vpc/02-plan-part1](screenshots/06-terraform-vpc/02-plan-part1.png)

**06-terraform-vpc/02-plan-part2**

![06-terraform-vpc/02-plan-part2](screenshots/06-terraform-vpc/02-plan-part2.png)

**06-terraform-vpc/02-plan-part3**

![06-terraform-vpc/02-plan-part3](screenshots/06-terraform-vpc/02-plan-part3.png)

**06-terraform-vpc/02-plan-part4**

![06-terraform-vpc/02-plan-part4](screenshots/06-terraform-vpc/02-plan-part4.png)

**06-terraform-vpc/03-apply-part1**

![06-terraform-vpc/03-apply-part1](screenshots/06-terraform-vpc/03-apply-part1.png)

**06-terraform-vpc/03-apply-part2**

![06-terraform-vpc/03-apply-part2](screenshots/06-terraform-vpc/03-apply-part2.png)

**06-terraform-vpc/03-apply-part3**

![06-terraform-vpc/03-apply-part3](screenshots/06-terraform-vpc/03-apply-part3.png)

**06-terraform-vpc/03-apply-part4**

![06-terraform-vpc/03-apply-part4](screenshots/06-terraform-vpc/03-apply-part4.png)

**06-terraform-vpc/03-apply-part5**

![06-terraform-vpc/03-apply-part5](screenshots/06-terraform-vpc/03-apply-part5.png)

**06-terraform-vpc/04-verify-aws-cli**

![06-terraform-vpc/04-verify-aws-cli](screenshots/06-terraform-vpc/04-verify-aws-cli.png)

**06-terraform-vpc/05-destroy-part1**

![06-terraform-vpc/05-destroy-part1](screenshots/06-terraform-vpc/05-destroy-part1.png)

**06-terraform-vpc/05-destroy-part2**

![06-terraform-vpc/05-destroy-part2](screenshots/06-terraform-vpc/05-destroy-part2.png)

**06-terraform-vpc/05-destroy-part3**

![06-terraform-vpc/05-destroy-part3](screenshots/06-terraform-vpc/05-destroy-part3.png)

**06-terraform-vpc/05-destroy-part4**

![06-terraform-vpc/05-destroy-part4](screenshots/06-terraform-vpc/05-destroy-part4.png)

**06-terraform-vpc/05-destroy-part5**

![06-terraform-vpc/05-destroy-part5](screenshots/06-terraform-vpc/05-destroy-part5.png)

**06-terraform-vpc/05-destroy-part6**

![06-terraform-vpc/05-destroy-part6](screenshots/06-terraform-vpc/05-destroy-part6.png)

**06-terraform-vpc/05-destroy-part7**

![06-terraform-vpc/05-destroy-part7](screenshots/06-terraform-vpc/05-destroy-part7.png)

**06-terraform-vpc/05-destroy-part8**

![06-terraform-vpc/05-destroy-part8](screenshots/06-terraform-vpc/05-destroy-part8.png)

**06-terraform-vpc/05-destroy-part9**

![06-terraform-vpc/05-destroy-part9](screenshots/06-terraform-vpc/05-destroy-part9.png)


## 07 Terraform workflow

`init → fmt → validate → plan → apply → output → state list → destroy` on a single S3 bucket (`session19-workflow-…`).

**07-terraform-workflow/01-workflow-part1**

![07-terraform-workflow/01-workflow-part1](screenshots/07-terraform-workflow/01-workflow-part1.png)

**07-terraform-workflow/01-workflow-part2**

![07-terraform-workflow/01-workflow-part2](screenshots/07-terraform-workflow/01-workflow-part2.png)

**07-terraform-workflow/01-workflow-part3**

![07-terraform-workflow/01-workflow-part3](screenshots/07-terraform-workflow/01-workflow-part3.png)

**07-terraform-workflow/01-workflow-part4**

![07-terraform-workflow/01-workflow-part4](screenshots/07-terraform-workflow/01-workflow-part4.png)


## 08 Mini project

Requirements: VPC `10.20.0.0/16`, public subnet `10.20.1.0/24`, IGW, public route table, association, and a web security group.

**Formatting finding.** `terraform fmt -check -recursive` exits with **3** and lists `main.tf`. The route block has an extra space (`gateway_id  =`). Running `terraform fmt` on a copy and diffing shows the one-line fix. The course file was not modified.

```diff
-    gateway_id  = aws_internet_gateway.main.id
+    gateway_id = aws_internet_gateway.main.id
```

`validate` → `plan` (6 to add) → `apply` → `output` / `state list`. The AWS CLI checks show `session19-mini-vpc` (10.20.0.0/16), `session19-mini-public-subnet`, `session19-mini-public-rt` and `session19-mini-web-sg`. Then `plan -destroy` / `destroy`.

**08-mini-project/01-fmt-finding**

![08-mini-project/01-fmt-finding](screenshots/08-mini-project/01-fmt-finding.png)

**08-mini-project/02-validate-plan-part1**

![08-mini-project/02-validate-plan-part1](screenshots/08-mini-project/02-validate-plan-part1.png)

**08-mini-project/02-validate-plan-part2**

![08-mini-project/02-validate-plan-part2](screenshots/08-mini-project/02-validate-plan-part2.png)

**08-mini-project/02-validate-plan-part3**

![08-mini-project/02-validate-plan-part3](screenshots/08-mini-project/02-validate-plan-part3.png)

**08-mini-project/02-validate-plan-part4**

![08-mini-project/02-validate-plan-part4](screenshots/08-mini-project/02-validate-plan-part4.png)

**08-mini-project/03-apply-part1**

![08-mini-project/03-apply-part1](screenshots/08-mini-project/03-apply-part1.png)

**08-mini-project/03-apply-part2**

![08-mini-project/03-apply-part2](screenshots/08-mini-project/03-apply-part2.png)

**08-mini-project/03-apply-part3**

![08-mini-project/03-apply-part3](screenshots/08-mini-project/03-apply-part3.png)

**08-mini-project/03-apply-part4**

![08-mini-project/03-apply-part4](screenshots/08-mini-project/03-apply-part4.png)

**08-mini-project/03-apply-part5**

![08-mini-project/03-apply-part5](screenshots/08-mini-project/03-apply-part5.png)

**08-mini-project/04-verify-aws-cli**

![08-mini-project/04-verify-aws-cli](screenshots/08-mini-project/04-verify-aws-cli.png)

**08-mini-project/05-destroy-part1**

![08-mini-project/05-destroy-part1](screenshots/08-mini-project/05-destroy-part1.png)

**08-mini-project/05-destroy-part2**

![08-mini-project/05-destroy-part2](screenshots/08-mini-project/05-destroy-part2.png)

**08-mini-project/05-destroy-part3**

![08-mini-project/05-destroy-part3](screenshots/08-mini-project/05-destroy-part3.png)

**08-mini-project/05-destroy-part4**

![08-mini-project/05-destroy-part4](screenshots/08-mini-project/05-destroy-part4.png)

**08-mini-project/05-destroy-part5**

![08-mini-project/05-destroy-part5](screenshots/08-mini-project/05-destroy-part5.png)

**08-mini-project/05-destroy-part6**

![08-mini-project/05-destroy-part6](screenshots/08-mini-project/05-destroy-part6.png)

**08-mini-project/05-destroy-part7**

![08-mini-project/05-destroy-part7](screenshots/08-mini-project/05-destroy-part7.png)

**08-mini-project/05-destroy-part8**

![08-mini-project/05-destroy-part8](screenshots/08-mini-project/05-destroy-part8.png)

**08-mini-project/05-destroy-part9**

![08-mini-project/05-destroy-part9](screenshots/08-mini-project/05-destroy-part9.png)


## 08 Optional extension: EC2

[ec2-extension/ec2.tf](ec2-extension/ec2.tf) is added next to a copy of the mini-project files:

```hcl
data "aws_ami" "al2023" { most_recent = true, owners = ["amazon"], filter al2023-ami-2023.*-x86_64 }
resource "aws_instance" "web" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id              # public subnet
  vpc_security_group_ids      = [aws_security_group.web.id]       # web SG
  associate_public_ip_address = true
}
```

Result: `Plan: 7 to add`, `Apply complete! Resources: 7 added`. `describe-instances` shows the instance `running` in the public subnet with a public IP. It was then destroyed and is `terminated`.

Answers to the extension questions:
1. **Which subnet?** The public subnet.
2. **Which security group?** `session19-mini-web-sg`.
3. **Why does a public subnet need a route to the IGW?** Without `0.0.0.0/0 → igw`, packets have no path out of the VPC, even if the instance has a public IP.
4. **What else is needed to reach the instance from the internet?** A public IP (or an Elastic IP), a security group rule for the port, a running service listening on it, and a network ACL that allows the traffic.
5. **Why not open SSH to `0.0.0.0/0`?** It exposes port 22 to brute-force attacks from the whole internet. Restrict it to your own IP, or use SSM Session Manager or a bastion host.

**08-ec2-extension/01-add-ec2-part1**

![08-ec2-extension/01-add-ec2-part1](screenshots/08-ec2-extension/01-add-ec2-part1.png)

**08-ec2-extension/01-add-ec2-part2**

![08-ec2-extension/01-add-ec2-part2](screenshots/08-ec2-extension/01-add-ec2-part2.png)

**08-ec2-extension/02-apply-part1**

![08-ec2-extension/02-apply-part1](screenshots/08-ec2-extension/02-apply-part1.png)

**08-ec2-extension/02-apply-part2**

![08-ec2-extension/02-apply-part2](screenshots/08-ec2-extension/02-apply-part2.png)

**08-ec2-extension/02-apply-part3**

![08-ec2-extension/02-apply-part3](screenshots/08-ec2-extension/02-apply-part3.png)

**08-ec2-extension/02-apply-part4**

![08-ec2-extension/02-apply-part4](screenshots/08-ec2-extension/02-apply-part4.png)

**08-ec2-extension/02-apply-part5**

![08-ec2-extension/02-apply-part5](screenshots/08-ec2-extension/02-apply-part5.png)

**08-ec2-extension/02-apply-part6**

![08-ec2-extension/02-apply-part6](screenshots/08-ec2-extension/02-apply-part6.png)

**08-ec2-extension/02-apply-part7**

![08-ec2-extension/02-apply-part7](screenshots/08-ec2-extension/02-apply-part7.png)

**08-ec2-extension/03-destroy-part1**

![08-ec2-extension/03-destroy-part1](screenshots/08-ec2-extension/03-destroy-part1.png)

**08-ec2-extension/03-destroy-part2**

![08-ec2-extension/03-destroy-part2](screenshots/08-ec2-extension/03-destroy-part2.png)

**08-ec2-extension/03-destroy-part3**

![08-ec2-extension/03-destroy-part3](screenshots/08-ec2-extension/03-destroy-part3.png)

**08-ec2-extension/03-destroy-part4**

![08-ec2-extension/03-destroy-part4](screenshots/08-ec2-extension/03-destroy-part4.png)

**08-ec2-extension/03-destroy-part5**

![08-ec2-extension/03-destroy-part5](screenshots/08-ec2-extension/03-destroy-part5.png)

**08-ec2-extension/03-destroy-part6**

![08-ec2-extension/03-destroy-part6](screenshots/08-ec2-extension/03-destroy-part6.png)


## Cleanup

All resources were destroyed. The `.terraform/` folders, state files, lock files and copied `terraform.tfvars` were deleted, and the emulator container was removed. `git status` shows only the new `homework/` folder.

**cleanup/01-cleanup**

![cleanup/01-cleanup](screenshots/cleanup/01-cleanup.png)


## Interview / practice answers

- **Route table vs security group:** a route table decides *where* packets go at the subnet level. A security group decides *whether* traffic is allowed at the instance level.
- **Stateful:** if inbound port 80 is allowed, the response goes out automatically without an outbound rule. Network ACLs are stateless.
- **Why Terraform for networking?** It makes the network repeatable, reviewable (`plan`) and easy to tear down (`destroy`). Six inter-dependent resources are created in the right order through implicit dependencies (`aws_vpc.main.id` references).
