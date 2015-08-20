# Docker Insurance - Backup solution

This tools backups Docker [volume containers](http://docs.docker.io/en/latest/use/working_with_volumes/#creating-and-mounting-a-data-volume-container)
and stores them on s3.

To use it, run:

    $ docker run -v /var/run/docker.sock:/docker.sock \
             -v /var/lib/docker/vfs/dir:/var/lib/docker/vfs/dir \
             -e ACCESS_KEY=... -e SECRET_KEY=... jangaraj/docker-insurance \
              s3://<BUCKET> container-a container-b container-c...

This will run tar and upload a tarball named after the container to S3.

Container uses environment variable, which can be overwritten:

| Variable | Default value | Description |
| -------- | ------------- | ----------- |
| PREFIX | "%Y-%m-%d_%H-%M-%S_" | Tarball prefix |
| SUFFIX | '' | Tarball suffix |
| DEBUG | 0 | Enable debug output (stdout) |
| PUSHGATEWAY | '' | Status reporting by HTTP request |
| S3CMD_OPTS | '' | Options for s3cmd command |
| ACCESS_KEY | '' | AWS S3 Access Key |
| SECRET_KEY | '' | AWS S3 Secret Key |
| EMAIL_FROM | '' | Sender of problem emails |
| EMAIL_TO | '' | Reciepient of problem emails |
| TIMEOUT | 0 | Backup period: 0 - one time backup only, 86400 = 24h |
| SMTP_SERVER | '' | SMTP server address |
| EXCLUDE | '' | Excluded volumes, e.g. '/etc/,/tmp'|

