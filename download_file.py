# created by Evan Delaney (evde) for the Volve dataset on 28 Aug 2018 - v0.1
# resume functionality enabled per Ming Wong's inquiry on Yammer
# brute force method
# many parts taken from stackoverflow
# other references:
# https://gist.github.com/mvpotter/9088499
# https://www.maketecheasier.com/split-download-large-file-curl/

# use "unzip foo_achive.zip" to unzip the downloaded filesize
# use "unzup foo_achive.zip foo_file.txt" to extract a certain file from foo_achive
# use "unzip -l foo_achive.zip" to list files in archive without extracting them

import requests
from pathlib import Path
import os
import time

#url = 'https://dataplatformblvolve.blob.core.windows.net/pub/Reservoir_Model-RMS_model_Volve.zip'
url = 'https://dataplatformblvolve.blob.core.windows.net/pub/Seismic.ST10010.zip'
#url = 'https://dataplatformblvolve.blob.core.windows.net/pub/Reports_Volve.zip'


def download_file(url, chunk_size = 2**30): # 2**30 corresponds to 1 GB chunks

    bytes_read = 0
    local_filename = url.split('/')[-1]
    cwd = os.getcwd()
    filecheck = Path(cwd + '/' + local_filename)
    if filecheck.is_file() == False:
        print('File does not exist... beginning download...')
        # taken from https://stackoverflow.com/questions/3620943/measuring-elapsed-time-with-the-time-module
        start_time = time.time()

        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        # taken from https://stackoverflow.com/questions/14270698/get-file-size-using-python-requests-while-only-getting-the-header
        filesize = float(r.headers['Content-length'])
        print('The file size is:')
        print(sizeof_fmt(filesize))

        with open(local_filename, 'wb') as f:
            i = 0
            for chunk in r.iter_content(chunk_size):
                if chunk: # filter out keep-alive new chunks
                    i += 1
                    bytes_read += len(chunk)
                    f.write(chunk)
                    f.flush()
                    download_per = float(bytes_read) / filesize * 100
                    print(sizeof_fmt(bytes_read) + ' of ' + sizeof_fmt(filesize) + '...' + ' %.2f' % download_per + '%')
                    elapsed_time = time.time() - start_time
                    print('Elapsed time: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + '\n')

        r.close()
        return local_filename


    elif filecheck.is_file() == True:
        print('File exists... resuming from appropriate byte position...')
        start_time = time.time()
        bytes_read = filecheck.stat().st_size
        print('We restart from byte position:')
        print(bytes_read)

        # NOTE the stream=True parameter
        # get original filesize first to note end point
        r = requests.get(url, stream=True)
        filesize = float(r.headers['Content-length'])

        if bytes_read >= filesize:
            raise ValueError('File appears to already be downloaded.')

        # taken from https://stackoverflow.com/questions/22894211/how-to-resume-file-download-in-python
        # now define range from resume point to end point
        resume_header = {'Range': 'bytes=%d-%d' % (bytes_read,filesize)}
        r = requests.get(url, headers = resume_header, stream=True)
        remaining_filesize = float(r.headers['Content-length'])
        print('The remaining file size is:')
        print(sizeof_fmt(remaining_filesize))

        with open(local_filename, 'ab') as f: # note that we use ab and not wb, for we want to append
            i = 0
            for chunk in r.iter_content(chunk_size):
                if chunk: # filter out keep-alive new chunks
                    i += 1
                    bytes_read += len(chunk)
                    f.write(chunk)
                    f.flush()
                    download_per = bytes_read / filesize * 100
                    print(sizeof_fmt(bytes_read) + ' of ' + sizeof_fmt(filesize) + '...' + ' %.2f' % download_per + '%')
                    elapsed_time = time.time() - start_time
                    print('Elapsed time: ' + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) + '\n')

        r.close()
        return local_filename

   # else:

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.3f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


download_file(url)
