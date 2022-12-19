# AWS Scripts

a set of tools to help you make daily basic annoying tasks on aws, the goal of the repository is to add more useful scripts, PR's are welcome! 😀

### Generate dynamodb tables in cloudformation format

```
usage: dynamodb_to_cf.py [-h] [--on-demand] [--region [REGION]] [--profile [PROFILE]]

optional arguments:
  -h, --help           show this help message and exit
  --on-demand          Use on-demand billing mode for the tables
  --region [REGION]
  --profile [PROFILE]
```

#### Usage

```bash
# generate cloudformation dynamodb tables from sa-east-1 with on demand provisioned of my_profile
python dynamodb_to_cf.py --region sa-east-1 --profile my_profile --on-demand
```
