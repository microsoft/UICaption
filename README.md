# UICaption dataset

We release the UICaption dataset consisting of UI images paired with descriptions of their functionality. This dataset was used to train Lexi, a pre-trained vision and language model for UI language understanding. The dataset and model are presented in "Lexi: Self-Supervised Learning of the UI Language" by Pratyay Banerjee, Shweti Mahajan, Kushal Arora, Chitta Baral, and Oriana Riva.

UICaption is released as a workflow by which you can generate the actual data. 

If you used this dataset please cite the following paper:

``` bibtex
@inproceedings{oriva:lexi22,
  title = {Lexi: Self-Supervised Learning of the UI Language},
  author = {Pratyay Banerjee and Shweti Mahajan and Kushal Arora and Chitta Baral and Oriana Riva},
  booktitle = {TBD},
  year = {2022},
  month = dec,
  doi = {TBD}
}
```

# Generate UICaption dataset

### Crawl images and texts from support websites

Use the compiled list of support and how-to websites provided in `tech_urls.txt` to extract UI images and associated descriptions from the web. Save the output to a folder, e.g., `crawled_uidata`:

```
python crawl_uidata.py -i tech_urls.txt -o crawled_uidata
```
This script will generate three files stored in the specified output folder: `ui_images.p` which contains URLs of the UI images, `ui_alt_texts.csv` which contains alt-text associated with each UI image, `ui_instructions_preceding.csv` and `ui_instructions_succeeding.csv` which contains texts appearing before and after the image occurence in the webpage respectively.

Then download the UI images:
```
python download_images.py -i crawled_uidata/ui_images.txt
```

### Generate image-text pairs

Finally, use the crawled UI data to assemble the UICaption dataset:
```
python gen_uicaption_dataset.py -i crawled_uidata -o ui_caption_dataset.json
```

The same UI image may appear in multiple websites, hence the script associates one or multiple alt-text descriptions and instructions with each UI image. The script produces a json file with the following format:

|Name|Description|
|----|-----------|
|image_path| path at which the UI image is stored|
|alt_text_list| one or multiple alt-texts associated with the UI image|
|instruction_list| one or more instructions associated with the UI image|


## Disclaimer

The code and dataset in this repository are intended to be used for research purposes. Microsoft takes no responsibility for what users use this tool for or for any damages caused from using this code. By downloading and using this software, you agree that you take full responsibility for any damages and liability.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
