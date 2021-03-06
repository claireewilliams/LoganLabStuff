#!/usr/bin/env python

import click
import os
import math
import time
import numpy as np
import pandas as pd
import qrcode
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

template_head = 'template_LCRY1700_head.tex'
template_tail = 'template_LCRY1700_tail.tex'
template_cols = 4
short_project_name = 'AplMicr'

def create_directory(project):

    # create directory for project labels
    newdir = 'labels_%s' % project
    if not os.path.exists(newdir):
        os.makedirs(newdir)

def make_label(project, contact, sample_type, date, sample, replicate, num_replicates, label_width, label_height):

    # generate text code and qr code
    # longcode = '%s_%s_%s_%s_%s_%01d' % (project, contact, sample_type, date, sample, replicate)
    if (num_replicates > 1):
        code = '%s_%s_%01d' % (short_project_name, sample, replicate)
        string = 'Project:%s\nContact:%s\nType:%s\nSample:%s\nReplicate:%01d' % (
            project, contact, sample_type,sample, replicate)
    else:
        code = '%s_%s' % (project, sample)
        longcode = '%s_%s_%s' % (short_project_name, sample_type, sample)
        string = '%s\n%s\nType:%s\nSample:%s\n%s' % (
            project, contact, sample_type, sample,longcode)

    # make qr code
    qr = qrcode.QRCode(
        #version=1, # set fit=True below to make this automatic
        error_correction=qrcode.constants.ERROR_CORRECT_L, # default is ERROR_CORRECT_M
        box_size=6, # number of pixels per box
        border=20, # larger border yields smaller qr code
    )
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # make label from qr code and string
    label = Image.new('RGB', (507, 225), color='white')
    #label.paste(img, (0,0))
    draw = ImageDraw.Draw(label)
    font = ImageFont.truetype('Monaco.dfont', 20)
    draw.text((10,10), string, (0,0,0), font=font)
    if (num_replicates > 1):
        label.save('labels_%s/label_%s_%01d.png'% (project, sample, replicate),dpi=(300,300))
    else:
        label.save('labels_%s/label_%s.png' % (project, sample),dpi=(300,300))

@click.command()
@click.option('--project', '-p', required=True, type=str,
              help="Short project name. Must not contain spaces.")
@click.option('--contact', '-c', required=True, type=str,
              help="Last name of point of contact. Must not contain spaces.")
@click.option('--sample_type', '-t', required=True, type=str,
              help="Type of sample (e.g. DNA/0.2um).")
@click.option('--date', '-d', required=False, type=str,
              help="Date (e.g. 2018-10-12).")
@click.option('--sample_list', '-l', required=False, type=click.Path(exists=True),
              help="List of samples. If none is provided, samples will be numbered 1 to num_samples.")
@click.option('--num_samples', '-s', required=False, type=int, default=5,
              help="Number of unique samples; ignored if sample_list provided. [default=5]")
@click.option('--num_replicates', '-r', required=False, type=int, default=1,
              help="Number of replicates per sample. [default=1 (i.e. no replicates)]")
@click.option('--label_width', '-w', required=False, type=float, default=1.05,
              help="Width of label in inches. 1.05 works for 1.28in labels. [default=1.05]")
@click.option('--label_height', '-h', required=False, type=float, default=0.5,
              help="Height of label in inches. 0.5 works for 0.5in labels. [default=0.5]")

def main(project, contact, sample_type, date, sample_list, num_samples, num_replicates, label_width, label_height):

    create_directory(project)

    # read sample list (and count number of samples) or number from 1 to num_samples
    if (sample_list):
        with open(sample_list, 'r') as f:
            samples = [line.rstrip() for line in f.readlines()]
            num_samples = len(samples)
    else:
        samples = [str(x).zfill(int(np.ceil(np.log10(num_samples+1)))) for x in np.arange(num_samples)+1]

    # make labels and latex table, iterating over sample numbers and replicates
    tex_table = {}
    num_sheets = math.ceil(num_samples * num_replicates / 52)
    for sheet in range(1, num_sheets + 1):
        tex_table[sheet] = ''
    tex_counter = 0
    for sample in samples:
        for replicate in np.arange(num_replicates) + 1:
            tex_counter += 1
            this_sheet = math.ceil(tex_counter / 52)
            make_label(project, contact, sample_type, date, sample, replicate, num_replicates, label_width, label_height)
            if (num_replicates > 1):
                tex_table[this_sheet] += '\\includegraphics[width=\\w, height=0.75in]{label_%s_%01d} & ' % (sample, replicate)
            else:
                tex_table[this_sheet] += '\\includegraphics[width=\\w,  height=0.75in]{label_%s} & ' % sample
            if ((tex_counter % template_cols) == 0):
                tex_table[this_sheet] = tex_table[this_sheet][:-2]
                tex_table[this_sheet] += '\\\\[\\h]\n'

    # make labelsheet latex file
    time.sleep(3)
    with open(template_head, 'r') as f:
        head = f.read()
    with open(template_tail, 'r') as f:
        tail = f.read()
    for sheet in range(1, num_sheets + 1):
        with open(f'labels_{project}/labelsheet{sheet}_{project}_LCRY1700.tex', 'w') as t:
            t.write(head)
            t.write(tex_table[sheet])
            t.write(tail)

if __name__ == "__main__":
    main()
