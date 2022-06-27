# -*- coding: utf-8 -*-
"""GenArtic Private

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HRpxztW8WJ1T9pQn708Mb7_Knx5pnnzI
"""

# Commented out IPython magic to ensure Python compatibility.
#@title Setup
nvidia_output = !nvidia-smi --query-gpu=memory.total --format=noheader,nounits,csv
gpu_memory = int(nvidia_output[0])
if gpu_memory < 14000:
  print(f"--> GPU check: ONLY {gpu_memory} MiB available: WARNING, some things might not work <--")
else:
  print(f"GPU check: {gpu_memory} MiB available: this should be fine")

print("Installing...")
from IPython.utils import io
with io.capture_output() as captured:
  !rm -Rf pixray
  !git clone --recursive --branch release https://github.com/pixray/pixray
  # Added for gui
  !echo "gradio" >> pixray/requirements.txt
  !pip install -r pixray/requirements.txt
  !pip install basicsr
  !pip install b2sdk
  !pip install emails
  !pip install python-dotenv
  !pip uninstall -y tensorflow
  !git clone https://github.com/pixray/diffvg
#   %cd diffvg
  !git submodule update --init --recursive
  !python setup.py install
#   %cd ..
  !pip freeze | grep torch
  !mkdir -p /content/models/

print("Downloading Models")
!wget -q --show-progress -nc -O /content/models/vqgan_coco.yaml https://dl.nmkd.de/ai/clip/coco/coco.yaml
!wget -q --show-progress -nc -O /content/models/vqgan_coco.ckpt https://dl.nmkd.de/ai/clip/coco/coco.ckpt

print("Installation Complete. Click Runtime>Restart and Run All")

#@title PixRay Gradio UI
import sys
sys.path.append("pixray")
import gradio as gr
import torch
import emails
import os, glob

from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/content/.env')
load_dotenv(dotenv_path=dotenv_path)

application_key_id = os.environ.get('B2_APPLICATION_KEY_ID')
application_key = os.environ.get('B2_APPLICATION_KEY')
bucket = os.environ.get('BUCKET')
ses_identity_sender = os.environ.get('SES_IDENTITY_SENDER')
ses_smtp_endpoint = os.environ.get('SES_SMTP_ENDPOINT')
ses_smtp_username = os.environ.get('SES_SMTP_USERNAME')
ses_smtp_password = os.environ.get('SES_SMTP_PASSWORD')
b2_friendly_url_hostname=os.environ.get('B2_FRIENDLY_URL_HOSTNAME')

try:
  torch.cuda.empty_cache()
except:
  print("Inoring GPU Error")

from b2sdk.v2 import B2Api
from b2sdk.v2 import InMemoryAccountInfo
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account("production", application_key_id, application_key)

def sync_to_b2(outputdir):
  from b2sdk.v2 import ScanPoliciesManager
  from b2sdk.v2 import parse_folder
  from b2sdk.v2 import Synchronizer
  from b2sdk.v2 import SyncReport
  from b2sdk.v2 import EncryptionSetting
  from b2sdk.v2 import EncryptionMode
  from b2sdk.v2 import BasicSyncEncryptionSettingsProvider
  from b2sdk.v2 import EncryptionAlgorithm
  import time
  import sys

  source = outputdir
  destination = os.path.join('b2://' + bucket + '/genartic/', os.path.basename(os.path.normpath(outputdir)))

  print("syncing: ")
  print(source)
  print("To: ")
  print(destination)

  source = parse_folder(source, b2_api)
  destination = parse_folder(destination, b2_api)

  policies_manager = ScanPoliciesManager(exclude_all_symlinks=True)

  synchronizer = Synchronizer(
    max_workers=10,
    policies_manager=policies_manager,
    dry_run=False,
    allow_empty_source=True,
  )

  no_progress = False
  encryptionsettings = EncryptionSetting(mode=EncryptionMode.SSE_B2,algorithm=EncryptionAlgorithm.AES256)
  encryption_settings_provider = BasicSyncEncryptionSettingsProvider(
    {
      bucket: encryptionsettings
    },
    {
      bucket: encryptionsettings
    }
  )
  with SyncReport(sys.stdout, no_progress) as reporter:
    synchronizer.sync_folders(
      source_folder=source,
      dest_folder=destination,
      now_millis=int(round(time.time() * 1000)),
      reporter=reporter,
      encryption_settings_provider=encryption_settings_provider,
    )

def notify(recipient, prompt, imagepath, videopath):
  sender = ses_identity_sender
  image = """https://%s/file/%s/genartic/%s""" % (b2_friendly_url_hostname,bucket,imagepath)
  video = """https://%s/file/%s/genartic/%s""" % (b2_friendly_url_hostname,bucket,videopath)

  body = """<p>Thank you for using GenArtic to create artwork for your prompt: </p>
  <br /><p>%s</p>
  <br />
  <br />
  <a href="%s">
  <img src="%s" />
  <br />Final Generated Image</a>
  <br />
  <br /><a href="%s">Video of all iterations</a>
  """ % (prompt, image, image, video)
  message = emails.html(
      html = body,
      subject = "GenArtic Generation is complete",
      mail_from = sender,
  )

  # Now you can send the email!
  r = message.send(
      to = recipient, 
      smtp = {
          "host": ses_smtp_endpoint, 
          "port": 587, 
          "timeout": 5,
          "user": ses_smtp_username,
          "password": ses_smtp_password,
          "tls": True,
      },
  )

# Define the main function
def generate(email, prompt, quality, style, aspect):
    import pixray
    if style == 'pixel':
      pixray.run(prompts=prompt,
                        drawer="pixel",
                        aspect=aspect,
                        quality=quality,
                        batches=2,
                        num_cuts=30,
                        iterations=100,
                        init_noise="snow",
                        clip_models='ViT-B/16',
                        make_video=True)
    
    if style == 'painting':
      pixray.run(prompts=prompt,
                        drawer="vqgan",
                        vqgan_model="coco",
                        aspect=aspect,
                        quality=quality,
                        batches=2,
                        num_cuts=30,
                        iterations=100,
                        init_noise="snow",
                        clip_models='ViT-B/16',
                        make_video=True)

    if style == 'clipdraw':
      pixray.run(prompts=prompt,
                        drawer="clipdraw",
                        aspect=aspect,
                        quality=quality,
                        batches=2,
                        num_cuts=30,
                        iterations=100,
                        init_noise="snow",
                        clip_models='ViT-B/16',
                        make_video=True)

    if style == 'line_sketch':
      pixray.run(prompts=prompt,
                        drawer="line_sketch",
                        aspect=aspect,
                        quality=quality,
                        batches=2,
                        num_cuts=30,
                        iterations=100,
                        init_noise="snow",
                        clip_models='ViT-B/16',
                        make_video=True)
    
    if style == 'image':
      pixray.run(prompts=prompt,
                        drawer="vqgan",
                        vqgan_model="imagenet_f16_16384",
                        aspect=aspect,
                        quality=quality,
                        batches=2,
                        num_cuts=30,
                        iterations=100,
                        init_noise="snow",
                        clip_models='ViT-B/16',
                        make_video=True)

    
    try:
      torch.cuda.empty_cache()
    except:
      print("Inoring GPU Error")


    # Find latest
    outdir=max(glob.glob(os.path.join("outputs", '*/')), key=os.path.getmtime)

    try:
      sync_to_b2(outdir)
    except:
      print("Inoring B2 Error")
    
    imagepath = os.path.join(outdir, 'output.png')
    videopath = os.path.join(outdir, 'output.mp4')

    try:
      notify(email, prompt, os.path.join(os.path.basename(os.path.normpath(outdir)),os.path.basename(imagepath)), os.path.join(os.path.basename(os.path.normpath(outdir)),os.path.basename(videopath)))
    except:
      print("Inoring SES Error")

    return imagepath, videopath 

# Create the UI
email = gr.Textbox(placeholder="youremail@youremail.com", label="Your Email Address to receive the completed generations")
prompt = gr.Textbox(value="Underwater city", label="Text Prompt")
quality = gr.Radio(choices=['draft', 'normal', 'better', 'best'], label="Quality")
style = gr.Radio(choices=['image', 'painting', 'pixel', 'clipdraw', 'line_sketch'], label="Type")
aspect = gr.Radio(choices=['square', 'widescreen','portrait'], label="Size")

# Launch the demo
iface = gr.Interface(fn=generate, inputs=[email, prompt, quality, style, aspect], outputs=[gr.Image(), gr.PlayableVideo()],live=False)
iface.launch(debug=True, share=True, enable_queue=True, server_port=8873, server_name="0.0.0.0")