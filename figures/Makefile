all: overview.png example.png

%.pdf: %.tex Makefile
	xelatex -shell-escape -interaction batchmode $<
	pdfcrop $@ $@

%.png: %.pdf Makefile
	convert -density 150 -trim $< -quality 100 -flatten $@

clean:
	rm -f *.pdf *.png *.log *.aux
