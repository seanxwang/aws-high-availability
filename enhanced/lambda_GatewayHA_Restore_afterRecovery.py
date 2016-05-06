from __future__ import print_function

import json
import boto3

print('Gateway HA - restore route table after recovery completes')
client = boto3.client('ec2', region_name='us-east-1')
    
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    #define current vpc and zone where squidnat failed
    eniId = event['detail']['requestParameters']['networkInterfaceId']
    eni = client.describe_network_interfaces(NetworkInterfaceIds=[eniId]).get('NetworkInterfaces')[0]
    
    vpc=eni.get('VpcId')
    zone = eni.get('AvailabilityZone')
    routetableFilters = [ {'Name':'vpc-id','Values':[vpc]}, {'Name':'tag:Zone','Values':[zone]}, {'Name':'tag:Name','Values':['private*']} ]
    #add err handling if results empty
    routetable = client.describe_route_tables(Filters=routetableFilters).get('RouteTables')[0].get('RouteTableId')

    #return to normal
    gateway_restore(routetable, eni)
    
    
def gateway_restore(routetable, eni):
    if (eni.get('Status') != 'in-use'):
        print ("eni status: " + eni.get('Status'))
    else:
        print ("Recovery completed... updating route table to use gateway in own zone")
        client.replace_route(RouteTableId=routetable, DestinationCidrBlock='0.0.0.0/0', NetworkInterfaceId=eni.get('NetworkInterfaceId'))
        print("Successfully updated route table to use gateway in own zone with " + eni.get('NetworkInterfaceId'))
