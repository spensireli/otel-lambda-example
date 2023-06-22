from aws_cdk import App
from deploys.dev import Deploy as DevDeploy, ENVIRONMENT as DEVENV

app = App()
dev_dataplane = DevDeploy(app, 'spenco', env=DEVENV)
app.synth()