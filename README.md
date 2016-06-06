# movingLabels
A simple Python script to generate moving labels using LibreOffice. Stores box and item information, plus current location, to SQLite3 database. The script was made to be able to scan boxes out of a house/apartment and into a new one, ensuring that the moving company doesn't have any that fall off the truck or are left behind. 

### Labels
For labels, I am using a Zebra printer (LP244x IIRC) with 4x6 labels, but can work with any printer that you can print from LibreOffice. The label file is saved as a flat XML file, allowing the script to modify it. The keywords used are:
- ((loc)) - The room where the box should be moved to
- ((floor)) - The floor where the box is going
- ((contents)) - The text area for contents(items) of the box
- ((BOX)) - Box number
 
The label was made using the standard Free 3 of 9 barcode font, but any barcode font will work (or feel free to omit the barcode). The label is created using LibreOffice Draw. 

#### Label printer?
You should be able to use any printer that you can print using LibreOffice. I really like thermal label printers, and you can get them for <$100 via the normal sources for used gear (ebay...). Labels are cheap, usually around $0.02 each when you buy a few rolls of 250. *Alternatively this can print to any printer, you choose the stock and label design. *

### Requirements and Installation
Was built for a Windows system, with Python 3.5.1 (any 3.1 or higher will work) and LibreOffice installed. This should work on other OSes, however it hasn't been tested yet. 

#### Notes
This may be a bit buggy, and currently has a few features that haven't been coded yet. The posted version functions for making boxes, adding items to a box, printing labels, and scanning items into/out of a location (e.g. inventory). Currently there is no way to view boxes or items except to print a label, and no way to edit. That's next. 
