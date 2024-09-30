### 1.put every md files into raw directory under root
# example 
    MultiModel_Rag
    ├── raw
        ├── xx.md
        ├── xx.md
        ├── xx.md
        ├── ...

### 2.run below bash file to convert files into embedding
# example
    bash ./scripts/md2knowledge.sh


### 3.run below bash file to process images in pdf
# example
    bash ./scripts/img2knowledge.sh
