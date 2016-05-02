# aws-high-availability
A high availability model for deploying any gateway appliances in AWS, with ASG, ENI and dynamic route table updates

What is this model for:
A basic model of deploying inline gateway in AWS, is to have a route pointing to gateway instance. To achieve HA, this model combines the use of
1) multiple gateway instances (one per AZ), corresponding to private route table per AZ
2) use of internal and external ENI (which are presistent regardless of instance failure)
3) use of ASG to monitor gateway health and auto recovery from failure
4) use of Lambda functions to switch route table target to use backup gateway during recovery, thus minimizing service down time

Why this model
