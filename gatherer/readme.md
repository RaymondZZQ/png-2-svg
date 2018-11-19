## Gather good training data
We want to have pixel-perfect copies of the same image in PNG and SVG format. To obtain these we will gather them from icon sites which provide icons in both formats.

First thought that comes to mind when gathering information from a site is making scrapers for them. I'm already familiar with Google's material ui icon set. This site seemed like a good source. However since dataset size is very important in training good deep neural nets, I also searched for other sites.

After looking at the top results and the ease of scraping the sites I found two other good sources: icons8 and iconfinder. I also noticed both of them offer an API for searching icons. This will simplify the gather process significantly.

So I end up with three sources:
- [Material Design Icons](https://material.io/tools/icons/)
- [Icons8](https://icons8.com) - [API](https://icons8.docs.apiary.io/#)
	- not all svg icons are free: so get 403 Forbidden for the svg icons
	- category: free-icons (10 000+)
	- free images are available to open-source projects
- [Iconfinder](https://www.iconfinder.com/) - [API](https://www.iconfinder.com/api-solution)

### Another key aspect of the training data is consistency. 
Two important aspects:
- resolution, as high as possible for png: -> rescale all to 128px
	- material ui: highest resolution is 48dpi and 2x -> 96x96 px
	- icons8: 500px
	- iconfinder: 
- colors?
	- material ui: no colors
	- icons 8:
	- iconfinder:

Resizing the image is done using *[Pillow](https://pillow.readthedocs.io/)*, a friendly Python Image Library fork.

### Enable resuming script
Save state at end and restore in order to allow script to be stopped and resumed later (so it will not download same images again)



