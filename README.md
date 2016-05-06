# aws-high-availability
A high availability model for deploying any gateway appliances in AWS, with ASG, ENI and dynamic route table updates

## What is this model for:
To achieve HA, this model combines the use of

1. multiple gateway instances (one per AZ), corresponding to private route table per AZ
2. use of internal and external ENI (which are presistent regardless of instance failure)
3. use of ASG to monitor gateway health and auto recovery from failure
4. use of Lambda functions to switch route table target to use backup gateway during recovery, thus minimizing service down time

For detailed explanation, please refer to
(http://www.seanxwang.com)

## Components:

#### Gateway ASG
ASG is created per AZ, defines a min and max of 1 instance for gateway, placed in that AZ's public subnet.

#### ENI
ENI is created per AZ, it is placed in that AZ's private subnet, which is used as target for default route.
Since ASG does not support ENI at launch, we must attach ENI to instance with bootstrapping as E1.

#### Route Table
Route table is created per AZ. The default route is persistent, its target is the ENI in that AZ.

#### Instance Bootstrapping
In addition to installing and configuring Gateway, gateway instance need to attach ENI as E1 (not supported via ASG)
      { "Fn::Join" : ["", [ "/usr/bin/aws ec2 attach-network-interface --network-interface-id ", { "Ref" : "GatewayENI" }, " --instance-id $INSTANCE_ID --device-index 1 --region ", { "Ref" : "AWS::Region" } ] ] },     

#### Gateway instance role
Gateway instance role allows instance to modify attribute and attach ENI
"GatewayRolePolicies": {
"Type": "AWS::IAM::Policy",
"Properties": {
"PolicyName": "root",
"PolicyDocument": {
"Version" : "2012-10-17",
"Statement": [ {
"Effect": "Allow",
"Action": [
"ec2:ModifyInstanceAttribute",
"ec2:AttachNetworkInterface"
],
"Resource": "*"
} ]
},
"Roles": [ { "Ref": "GatewayRole" } ]
}
},
