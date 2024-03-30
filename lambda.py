
import boto3
from datetime import datetime, timedelta, timezone


def getec2list():
    
    mysns = "arn:aws-cn:sns:cn-northwest-1:000000000000:ec2runmax"
    
    session = boto3.Session(region_name='cn-northwest-1')
    ec2 = session.client('ec2')
    notifymsg = ""
    # Filter instances by instance type
    instances = ec2.describe_instances(Filters=[
        {
            'Name': 'instance-type',
            'Values': ['t3.*']
        }
    ])['Reservations']

    # Calculate the cutoff time (1 day ago)
    UTC = timezone(timedelta(hours=+0))
    #cutoff_time = datetime.now(UTC) - timedelta(days=1)
    cutoff_time = datetime.now(UTC) - timedelta(minutes=1)

    
    # Iterate over instances and print name and private IP if start time is greater than cutoff
    for reservation in instances:
        for instance in reservation['Instances']:
            if reservation['Instances'][0]['State']['Name'] == 'running':
                isprod = 0
                for tag in instance['Tags']:
                    if tag['Key'] == 'prod':
                        tagvalue = tag['Value']
                        if tagvalue == 1:
                            isprod =1
                if isprod != 1:
                    launch_time = instance['LaunchTime']
                    if launch_time < cutoff_time:
                        instance_name = instance.get('PrivateDnsName', 'No Name')
                        private_ip = instance['PrivateIpAddress']
                        #print(f"Instance Name: {instance_name}, Private IP: {private_ip}")
                        notifymsg = "%s Instance Name: %s Private IP:%s \n" %(notifymsg,instance_name,private_ip)
                                
    snsclient =session.client('sns')
    snsArn = mysns
    snsmsg = "You have ec2 Running for longer than expected duration \n %s",%(notifymsg)
    response = snsclient.publish(TopicArn=snsArn,Message=snsmsg,Subject='Warnning')
    print(response["MessageId"])
    

def lambda_handler(event, context):
    getec2list()

