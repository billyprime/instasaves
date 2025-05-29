# instasaves
A python script to download your Instagram saved posts

To use this script, you'll need to [download a copy of your data from Instagram](https://help.instagram.com/181231772500920?helpref=faq_content).  

## Details

When downloading your "takeout data" from IG, it does not make copies of your saved posts.  This script will download images you've saved.  

Note that there are some significant restrictions here:

* It will only download public photos.
* It will not download private or 18+ photos.
* It will not download reels or videos.
* Sometimes it downloads the wrong photo because of the mess that is Instagram's source code.

The script has a built-in retry feature, but you may need to force-stop it if it gets stuck for some reason (this happened a couple times when I was testing). 

These are known issues, and by using the tool you agree to not complain about them.  (Pull requests welcome, of course.)

## Installation

Run `pip install -r requirements.txt`  per usual.  (You probably will want a virtual environment of some sort.)

## Usage

`python scrape.py /path/to/your_instagram_activity/saved/saved_collections.html /my/output/directory/`

If you have lots of saved posts, you may need to run this a couple of times in a row, just in case of any network weirdnesses that might have exceeded the built-in retries.

