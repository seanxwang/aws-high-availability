from __future__ import print_function

import json
import boto3
import time

print('Gateway HA test - failover during recovery')
client = boto3.client('ec2', region_name='us-east-1')
    
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    #define current vpc and zone where gateway failed
    subnetid = event['detail']['Details']['Subnet ID']
    zone = event['detail']['Details']['Availability Zone']
    vpc=client.describe_subnets(SubnetIds=[subnetid]).get('Subnets')[0].get('VpcId')
    
    print("Gateway ASG recovering in...")
    print("region = " + event['region'])
    print("VPC=" + vpc)
    print("zone = " + zone)
    print("subnet = " + subnetid)
    
    #define zone and route table for interim failover
    if zone.endswith('a'):
        zone_failover=zone[:-1] +'b'
        print("failover zone:" + zone_failover)
    if zone.endswith('b'):
        zone_failover=zone[:-1] +'a'
        print("failover zone:" + zone_failover)
    
    #get gateway eni    
    eni_Filters=[ {'Name':'vpc-id','Values':[vpc]}, {'Name':'availability-zone','Values':[zone]}, {'Name':'tag:Name','Values':['Gateway-eni*']} ]
    eni = client.describe_network_interfaces(Filters=eni_Filters).get('NetworkInterfaces')[0]
    eni_failover_Filters=[ {'Name':'vpc-id','Values':[vpc]}, {'Name':'availability-zone','Values':[zone_failover]}, {'Name':'tag:Name','Values':['Gateway-eni*']} ]
    eni_failover = client.describe_network_interfaces(Filters=eni_failover_Filters).get('NetworkInterfaces')[0]

    #update private route table to point to failover eni    
    routetableFilters = [ {'Name':'vpc-id','Values':[vpc]}, {'Name':'tag:Zone','Values':[zone]}, {'Name':'tag:Name','Values':['private*']} ]
    routetable = client.describe_route_tables(Filters=routetableFilters).get('RouteTables')[0].get('RouteTableId')
    print("Recovery in progress... updating route table " + routetable + " to use gateway in neighbor zone before recovery completes")
    
    #failover
    gateway_failover(routetable, eni_failover)
    
def gateway_failover(routetable, eni_failover):
    client.replace_route(RouteTableId=routetable, DestinationCidrBlock='0.0.0.0/0', NetworkInterfaceId=eni_failover.get('NetworkInterfaceId'))
    print("Successfully updated route table to use gateway in failover zone with " + eni_failover.get('NetworkInterfaceId'))
