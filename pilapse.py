#!/usr/bin/env python3
#
# Matthew Giarra
# matthew.giarra@gmail.com
# First commit 2020-05-03
#

import argparse
from time import sleep
from picamera import PiCamera
from datetime import datetime, timedelta
import os
import pdb

# This function converts a formatted string to a datetime object
def str2date(s):
    return datetime.strptime(s, '%Y-%m-%d-%H-%M-%S') 

def date2str(d):
    return(d.strftime('%Y-%m-%d %H:%M:%S'))

# This function converts a string to a datetime object 
# if the string matches a specified format, and errors otherwise
def valid_date(s):
    try:
        #return datetime.strptime(s, '%Y-%m-%d-%H-%M-%S')
        return(str2date(s))
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

# Main function 
def main():

    # Get the time now
    nowtime=datetime.now()

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', '-o', type=str, default='.', help='Directory for saving images' )
    parser.add_argument('-s', '--start', type=valid_date, default=nowtime, 
            help='Start date and time, formatted as YYYY-MM-DD-HH-MM-SS (Default: start immediately)')
    parser.add_argument('-d', '--duration', type=float, default = 0, 
            help='Duration of time series in units specified by --unit. Runs forever if unset.')
    parser.add_argument('-i', '--interval', type=float, default=1,
            help='Time lapse interval in units specified by --unit (Default: 1)')
    parser.add_argument('-u', '--unit', choices = ['hours', 'minutes', 'seconds', 'Hours', 'Minutes', 'Seconds'], 
            default='seconds', help='Time unit (seconds, hours, or minutes) (Default: seconds)') 

    args, leftovers = parser.parse_known_args()
    outdir = args.outdir
    duration = args.duration
    interval = args.interval if args.interval > 0 else 1
    unit = args.unit.lower()
    date_start=args.start

    # Make output directory if it doesn't exist
    if not(os.path.isdir(outdir)):
            os.makedirs(outdir, exist_ok=True)

    # Start time in the past so start now
    if date_start < nowtime:
        print('Warning: start time occurs in the past. Starting now.')
        date_start = nowtime

    # Figure out end datetime from specified time units
    if unit=='seconds':
        date_end = date_start + timedelta(seconds = duration)
        interval_sec = interval
    elif unit == 'minutes':
        date_end = date_start + timedelta(minutes = duration)
        interval_sec = interval * 60
    elif unit == 'hours':
        date_end = date_start + timedelta(hours = duration)
        interval_sec = interval * 3600

    # Print a summary
    print('\nTime lapse summary:')
    print('Start date/time: %s' % date2str(date_start))
    print('End date/time: ', end='')
    print('%s' % date2str(date_end) if duration > 0 else 'never')
    print('Time lapse duration: ', end='')
    print('%0.2f %s' % (duration, unit) if duration > 0 else 'forever')
    print('Time lapse interval: %0.2f %s' % (interval, unit))
    print('Image save directory: %s' % os.path.abspath(outdir))

    # Set up the camera
    camera = PiCamera()
    camera.start_preview()
    sleep(2)

    # Main loop
    while True:
        # Get the time this iteration
        nowtime = datetime.now()

        # Exit if we're past the end time
        if((duration > 0) & (nowtime > date_end)):
            print('Done!')
            return
        
        # Keep going if we haven't reached the end time
        if nowtime >= date_start:
            camera.annotate_text = nowtime.strftime("%A %B %d %Y %I:%M:%S %p")        
            outname = nowtime.strftime("%Y-%m-%d_%H-%M-%S.jpg")
            outpath = os.path.join(outdir, outname)
            camera.capture(outpath)
            if os.path.isfile(outpath):
                print('Saved image: %s' % outpath)
            else:
                print('Failed to save image: %s' % outpath)
            sleep(interval_sec) 
        
        # Print a message and wait if we're still waiting for start time
        else:
           time_remaining = date_start - nowtime
           print("Starting time lapse in %s" % str(time_remaining))
           sleep(2)

if __name__ == '__main__':
    main()
