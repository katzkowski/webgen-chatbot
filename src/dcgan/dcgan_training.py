#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

#%matplotlib inline
import logging
import logging.config
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
from dotenv import load_dotenv
from PIL import ImageFile

load_dotenv()
ImageFile.LOAD_TRUNCATED_IMAGES = False

DATA_PATH = Path(os.getenv("DATA_PATH"))
LOGS_PATH = os.getenv("LOGS_PATH")
PLOT_PATH = DATA_PATH / "plots"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "basic": {"format": "%(name)s - %(levelname)s - %(message)s"},
        "extended": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "extended",
            "filename": str(
                Path(LOGS_PATH) / "{:%Y-%m-%d_%H-%M-%S}.log".format(datetime.now())
            ),
        },
    },
    "loggers": {
        "training": {
            "level": "INFO",
            "handlers": ["console", "file_handler"],
            "propagate": False,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}

log = None

# Set random seed for reproducibility
manualSeed = 999
# manualSeed = random.randint(1, 10000) # use if you want new results
# print("Random Seed: ", manualSeed)
random.seed(manualSeed)
torch.manual_seed(manualSeed)

# Number of workers for dataloader
workers = None

# Batch size during training
batch_size = 128  # 128 -> 64 -> 32 -> 16

# Spatial size of training images. All images will be resized to this
#   size using a transformer.
image_size = 128  # dim changed

# Number of channels in the training images. For color images this is 3
nc = 3

# Size of z latent vector (i.e. size of generator input)
nz = 100

# Size of feature maps in generator
ngf = 128  # dim changed

# Size of feature maps in discriminator
ndf = 128  # dim changed

# Number of training epochs
num_epochs = 0

# Learning rate for optimizers
lr = 0.0002

# Beta1 hyperparam for Adam optimizers
beta1 = 0.5

# Number of GPUs available. Use 0 for CPU mode.
ngpu = 1

# Different backend that does not show plots to user
matplotlib.use("Agg")


class Discriminator(nn.Module):
    def __init__(self, ngpu):
        super(Discriminator, self).__init__()
        self.ngpu = ngpu
        self.main = nn.Sequential(
            # input is (nc) x 64 x 64
            nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf) x 32 x 32
            nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 2),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*2) x 16 x 16
            nn.Conv2d(ndf * 2, ndf * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 4),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*4) x 8 x 8
            nn.Conv2d(ndf * 4, ndf * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ndf * 8),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*8) x 4 x 4
            nn.Conv2d(ndf * 8, ndf * 16, 4, stride=2, padding=1, bias=False),

            # extra layer
            nn.BatchNorm2d(ndf * 16),
            nn.LeakyReLU(0.2, inplace=True),
            # state size. (ndf*16) x 4 x 4
            nn.Conv2d(ndf * 16, 1, 4, stride=1, padding=0, bias=False),

            nn.Sigmoid(),
        )

    def forward(self, input):
        return self.main(input)


class Generator(nn.Module):
    def __init__(self, ngpu):
        super(Generator, self).__init__()
        self.ngpu = ngpu
        self.main = nn.Sequential(
            # input is Z, going into a convolution
            nn.ConvTranspose2d(nz, ngf * 16, 4, 1, 0, bias=False),  # ngf factor 8 -> 16
            nn.BatchNorm2d(ngf * 16),  # 8 -> 16
            nn.ReLU(True),
            # state size. (ngf*8) x 4 x 4
            nn.ConvTranspose2d(
                ngf * 16, ngf * 8, 4, 2, 1, bias=False
            ),  # ngf factor: 8 -> 16, 4 -> 8
            nn.BatchNorm2d(ngf * 8),  # 4 -> 8
            nn.ReLU(True),
            # state size. (ngf*4) x 8 x 8
            nn.ConvTranspose2d(
                ngf * 8, ngf * 4, 4, 2, 1, bias=False
            ),  # ngf factor: 4 -> 8, 2 -> 4
            nn.BatchNorm2d(ngf * 4),  # 2 -> 4
            nn.ReLU(True),
            # == extra layer end ==
            # state size. (ngf*4) x 16 x 16

            nn.BatchNorm2d(ngf * 4),
            nn.ReLU(True),
            # state size. (ngf*4) x 8 x 8
            nn.ConvTranspose2d(ngf * 4, ngf * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.ReLU(True),
            # state size. (ngf*2) x 16 x 16
            nn.ConvTranspose2d(ngf * 2, ngf, 4, 2, 1, bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(True),
            # state size. (ngf) x 32 x 32
            nn.ConvTranspose2d(ngf, nc, 4, 2, 1, bias=False),
            nn.Tanh()
            # state size. (nc) x 64 x 64
        )

    def forward(self, input):
        return self.main(input)


def weights_init(m):
    # custom weights initialization called on netG and netD
    classname = m.__class__.__name__
    if classname.find("Conv") != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find("BatchNorm") != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)


def load_dataset(model_name: str, model_annotation: str = None):
    # Root directory for dataset
    dataroot = str(Path(DATA_PATH) / "datasets" / ("dataset_" + model_name + "_root"))

    # Create the dataset
    dataset = dset.ImageFolder(
        root=dataroot,
        transform=transforms.Compose(
            [
                transforms.Resize(image_size),
                transforms.CenterCrop(image_size),
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        ),
    )
    # Create the dataloader
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=True, num_workers=workers
    )

    print(len(dataset))
    log.info(f"Using dataset from {dataroot} with length {len(dataset)}")

    # Plot some training images
    real_batch = next(iter(dataloader))
    plt.figure(figsize=(8, 8))
    plt.axis("off")
    plt.title("Training Images")
    plt.imshow(
        np.transpose(
            vutils.make_grid(
                real_batch[0].to(device)[:64], padding=2, normalize=True
            ).cpu(),
            (1, 2, 0),
        )
    )

    if model_annotation is None:
        os.mkdir(PLOT_PATH / (model_name + "_" + str(num_epochs)))
        plt.savefig(
            PLOT_PATH / (model_name + "_" + str(num_epochs)) / "training_imgs.pdf"
        )
    else:
        os.mkdir(
            PLOT_PATH / (model_name + "_" + model_annotation + "_" + str(num_epochs))
        )
        plt.savefig(
            PLOT_PATH
            / (model_name + "_" + model_annotation + "_" + str(num_epochs))
            / "training_imgs.pdf"
        )
    return dataloader


def init_training():
    global log

    # initalize logging
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger("training")

    log.info("Starting program")

    # check if model has been specified
    if len(sys.argv) == 1:
        log.critical("No model specified, exiting program.")
        exit(1)

    # get model name
    model_name = sys.argv[1]

    # get epoch amount
    epochs = int(sys.argv[2])

    # get workers amount
    global workers
    workers = int(sys.argv[3])

    try:
        model_annotation = sys.argv[4]
    except IndexError:
        log.warning(f"No model annotation specified")
        log.info(
            f"Running training for model {model_name} for {epochs} epochs with {workers} dataloader workers."
        )
        run_training(model_name, epochs)
    else:
        log.info(
            f"Running training for model {model_name} annotated with {model_annotation} for {epochs} epochs with {workers} dataloader workers."
        )
        run_training(model_name, epochs, model_annotation)


def run_training(model_name: str, epochs: int, model_annotation: str = None):
    global num_epochs, device
    num_epochs = epochs

    # Decide which device we want to run on
    device = torch.device(
        "cuda:0" if (torch.cuda.is_available() and ngpu > 0) else "cpu"
    )

    if str(device) != "cuda:0":
        log.critical(f"Not training on GPU, but instead on {device}")
        log.critical("Exiting program")
        exit(1)

    dataloader = load_dataset(model_name, model_annotation)
    # Create the generator
    netG = Generator(ngpu).to(device)

    # Handle multi-gpu if desired
    if (device.type == "cuda") and (ngpu > 1):
        netG = nn.DataParallel(netG, list(range(ngpu)))

    # Apply the weights_init function to randomly initialize all weights
    #  to mean=0, stdev=0.2.
    netG.apply(weights_init)

    # Print the model
    print(netG)
    log.info(netG)

    # Create the Discriminator
    netD = Discriminator(ngpu).to(device)

    # Handle multi-gpu if desired
    if (device.type == "cuda") and (ngpu > 1):
        netD = nn.DataParallel(netD, list(range(ngpu)))

    # Apply the weights_init function to randomly initialize all weights
    #  to mean=0, stdev=0.2.
    netD.apply(weights_init)

    # Print the model
    print(netD)
    log.info(netD)

    # Initialize BCELoss function
    criterion = nn.BCELoss()

    # Create batch of latent vectors that we will use to visualize
    #  the progression of the generator
    fixed_noise = torch.randn(128, nz, 1, 1, device=device)  # dim changed

    # Establish convention for real and fake labels during training
    real_label = 1.0
    fake_label = 0.0

    # Setup Adam optimizers for both G and D
    optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(beta1, 0.999))
    optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(beta1, 0.999))

    # Training Loop

    # Lists to keep track of progress
    img_list = []
    G_losses = []
    D_losses = []
    iters = 0

    log.info("Starting Training Loop...")
    print("Starting Training Loop...")
    # For each epoch
    for epoch in range(num_epochs):
        # For each batch in the dataloader
        for i, data in enumerate(dataloader, 0):
            # log.info(f"[{epoch}/{num_epochs}][{i}/{len(dataloader)}]")
            ############################
            # (1) Update D network: maximize log(D(x)) + log(1 - D(G(z)))
            ###########################
            ## Train with all-real batch
            netD.zero_grad()
            # Format batch
            real_cpu = data[0].to(device)
            b_size = real_cpu.size(0)
            label = torch.full((b_size,), real_label, dtype=torch.float, device=device)
            # Forward pass real batch through D
            output = netD(real_cpu).view(-1)
            # Calculate loss on all-real batch
            errD_real = criterion(output, label)
            # Calculate gradients for D in backward pass
            errD_real.backward()
            D_x = output.mean().item()

            ## Train with all-fake batch
            # Generate batch of latent vectors
            noise = torch.randn(b_size, nz, 1, 1, device=device)
            # Generate fake image batch with G
            fake = netG(noise)
            label.fill_(fake_label)
            # Classify all fake batch with D
            output = netD(fake.detach()).view(-1)
            # Calculate D's loss on the all-fake batch
            errD_fake = criterion(output, label)
            # Calculate the gradients for this batch, accumulated (summed) with previous gradients
            errD_fake.backward()
            D_G_z1 = output.mean().item()
            # Compute error of D as sum over the fake and the real batches
            errD = errD_real + errD_fake
            # Update D
            optimizerD.step()

            ############################
            # (2) Update G network: maximize log(D(G(z)))
            ###########################
            netG.zero_grad()
            label.fill_(real_label)  # fake labels are real for generator cost
            # Since we just updated D, perform another forward pass of all-fake batch through D
            output = netD(fake).view(-1)
            # Calculate G's loss based on this output
            errG = criterion(output, label)
            # Calculate gradients for G
            errG.backward()
            D_G_z2 = output.mean().item()
            # Update G
            optimizerG.step()

            # Output training stats
            if i % 50 == 0:
                log.info(
                    "[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f\tD(x): %.4f\tD(G(z)): %.4f / %.4f"
                    % (
                        epoch,
                        num_epochs,
                        i,
                        len(dataloader),
                        errD.item(),
                        errG.item(),
                        D_x,
                        D_G_z1,
                        D_G_z2,
                    )
                )
                print(
                    "[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f\tD(x): %.4f\tD(G(z)): %.4f / %.4f"
                    % (
                        epoch,
                        num_epochs,
                        i,
                        len(dataloader),
                        errD.item(),
                        errG.item(),
                        D_x,
                        D_G_z1,
                        D_G_z2,
                    )
                )

            # Save Losses for plotting later
            G_losses.append(errG.item())
            D_losses.append(errD.item())

            # Check how the generator is doing by saving G's output on fixed_noise
            if (iters % 500 == 0) or (
                (epoch == num_epochs - 1) and (i == len(dataloader) - 1)
            ):
                with torch.no_grad():
                    fake = netG(fixed_noise).detach().cpu()
                img_list.append(vutils.make_grid(fake, padding=2, normalize=True))

            iters += 1

    log.info("Training completed")

    # training loss plot
    plt.figure(figsize=(10, 5))
    plt.title("Generator and Discriminator Loss During Training")
    plt.plot(G_losses, label="G")
    plt.plot(D_losses, label="D")
    plt.xlabel("iterations")
    plt.ylabel("Loss")
    plt.legend()

    # save plot
    if model_annotation is None:
        plt.savefig(
            PLOT_PATH / (model_name + "_" + str(num_epochs)) / "training_loss.pdf"
        )
    else:
        plt.savefig(
            PLOT_PATH
            / (model_name + "_" + model_annotation + "_" + str(num_epochs))
            / "training_loss.pdf"
        )

    # training animation
    fig = plt.figure(figsize=(16, 16))
    plt.axis("off")
    ims = [[plt.imshow(np.transpose(i, (1, 2, 0)), animated=True)] for i in img_list]
    ani = animation.ArtistAnimation(
        fig, ims, interval=1000, repeat_delay=1000, blit=True
    )

    # only in ipynb
    # HTML(ani.to_jshtml())

    # save animation
    if model_annotation is None:
        with open(
            PLOT_PATH / (model_name + "_" + str(num_epochs)) / "animation.html",
            "w",
        ) as ani_file:
            print(ani.to_html5_video(embed_limit=200.0), file=ani_file)

    else:
        with open(
            PLOT_PATH
            / (model_name + "_" + model_annotation + "_" + str(num_epochs))
            / "animation.html",
            "w",
        ) as ani_file:
            print(ani.to_html5_video(embed_limit=200.0), file=ani_file)

    # Grab a batch of real images from the dataloader
    real_batch = next(iter(dataloader))

    # Plot the real images
    plt.figure(figsize=(15, 15))
    plt.subplot(1, 2, 1)
    plt.axis("off")
    plt.title("Real Images")
    plt.imshow(
        np.transpose(
            vutils.make_grid(
                real_batch[0].to(device)[:64], padding=5, normalize=True
            ).cpu(),
            (1, 2, 0),
        )
    )

    # # save plot
    # if model_annotation is None:
    #     plt.savefig(PLOT_PATH / (model_name + "_" + str(num_epochs)) / "real_fake.pdf")
    # else:
    #     plt.savefig(
    #         PLOT_PATH
    #         / (model_name + "_" + model_annotation + "_" + str(num_epochs))
    #         / "real_fake.pdf"
    #     )

    # Plot the fake images from the last epoch
    plt.subplot(1, 2, 2)
    plt.axis("off")
    plt.title("Fake Images")
    plt.imshow(np.transpose(img_list[-1][:64], (1, 2, 0)))

    # save plot
    if model_annotation is None:
        plt.savefig(PLOT_PATH / (model_name + "_" + str(num_epochs)) / "real_fake_imgs.pdf")
    else:
        plt.savefig(
            PLOT_PATH
            / (model_name + "_" + model_annotation + "_" + str(num_epochs))
            / "real_fake_imgs.pdf"
        )

    # create path for model
    if model_annotation is None:
        model_path = str(
            DATA_PATH / "models" / (model_name + "_" + str(num_epochs) + ".pth")
        )
    else:
        model_path = str(
            DATA_PATH
            / "models"
            / (model_name + "_" + model_annotation + "_" + str(num_epochs) + ".pth")
        )
    log.info("Plots saved")

    # save model
    torch.save(
        {
            "discriminator_state_dict": netD.state_dict(),
            "generator_state_dict": netG.state_dict(),
            "optimizerD_state_dict": optimizerD.state_dict(),
            "optimizerG_state_dict": optimizerG.state_dict(),
        },
        model_path,
    )
    log.info("Model saved")


if __name__ == "__main__":
    init_training()
