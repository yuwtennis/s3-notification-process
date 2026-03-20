# s3-notification-process

Example repository for processing s3 notifications using Lambda function.  

## Quick architecture

```markdown
s3 ---> sqs <--- lambda
```

- lambda is decoupled from s3 for maintainability and scalability