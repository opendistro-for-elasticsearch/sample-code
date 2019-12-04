# ANT332 - Use Amazon ES to visualize and monitor containerized applications

This folder contains lab materials for ANT332 workshop conducted at AWS re:Invent 2019.

All CloudFormation templates used to spin up the workshop environment can be found under the `cloudformation` sub-directory.

This sub-directory contains a `child-stacks` folder, which are stacks hosted by the ANT332 team in an S3 bucket.

These S3 hosted stacks are referenced as ***nested*** CloudFormation stacks under the `parent-stack` sub-directory, in the `root-new.yml` template.

### AWS Region Support

This lab environment setup is currently only supported in the `eu-west-1` region.

The setup will ***not*** work if you deploy in any other region.

We plan on adding support for other regions in the future.

### Deployment

To deploy the environment, you can simply upload the `parent-stack/root-new.yml` CloudFormation template into your CloudFormation Console.

CloudFormation will ask you to provide a `Cloud9IAMPrincipalARN` parameter.

This parameter is ***required*** to gain access to the deployed Cloud9 IDE instance.

This parameter should be the IAM principal (IAM assumed-role/user/federated-user) you are using to login to your AWS console.

More details on the values this parameter can accept are provided [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloud9-environmentec2.html#cfn-cloud9-environmentec2-ownerarn). The lab setup will not work if this parameter is incorrect.

We highly ***discourage*** changing anything in the nested child stacks as the setup may not work.

The deployment takes roughly 30 minutes to fully deploy and provision underlying resources.

This includes an AWS Cloud9 IDE, an Amazon EKS cluster with 4 worker nodes and a Amazon Elasticsearch domain.

Please follow the instructions provided in our [ANT332 Lab Guide](http://eseksworkshop.com) to start the lab after the CloudFormation finishes deploying.

Please create an issue under this repository if you have any trouble and one of the contributors for this workshop will happily assist you.
