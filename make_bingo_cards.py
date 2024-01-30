'''
Script to make Bingo cards
'''

import argparse
from collections import OrderedDict
from math import ceil, floor
from random import randint, shuffle
from copy import deepcopy

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.tight_layout import get_renderer

# Constants
# Default values
#   card size = number of card rows x columns
#   card title = card title string
#   multiLineFontSize = font size of text that occupies multiple lines
#     of a card space
#   out file = output file name containing generated bingo cards
# Default 
DEFAULTS = {
    'card size': '5x5',
    'cards per page': 4,
    'column labels': 'B,I,N,G,O',
    'multiLineFontSize': 12,
    'out file': 'bingo_cards.pdf'}


def make_cards(valuesDict, nCards, cardSize=DEFAULTS['card size'],
        cardTitle=None,
        columnLabelList=DEFAULTS['column labels'].split(','),
        multiLineFontSize=DEFAULTS['multiLineFontSize'],
        nCardsPerPage=DEFAULTS['cards per page'],
        outFile=DEFAULTS['out file'], scatter=False, useFreeSpace=True):
    '''
    Creates bingo cards and writes them to a PDF file.
    INPUT
    - valuesDict = dict containing values to populate card spaces with.
        The keys are column labels and the value of each key is a list
        containing values for that column. If columns are not used,
        there is a single key (None) and all the card values are
        contained in a list that is the key value.
    - nCards = number of cards to generate
    - cardSize = Number of rows and columns of each card. Valid values
        values are "3x3", "4x4", and "5x5".
    - cardTitle = string containing the card title. If a title is not
        used, use None.
    - columnLabelList = list where each element printed at the top of
        each card column. To not use card column labels, use None.
    - multiLineFontSize = font size for text that occupies multiple
        lines of a card space
    - nCardsPerPage = Number of bingo cards per printed page. Valid
        values are 1, 2, and 4.
    - outFile = name of output PDF file containing cards
    - scatter = True / False, True will scatter the values around the
        card. False will randomize card values only within their own
        columns.
    - useFreeSpace = True / False, True will put a free space at the
        center of each card. If the number of rows is 4, the free space
        will be randomly selected.    
    '''
    # Map the number of cards per page to the number of axes rows and
    # columns that can be used in the call to plt.subplots(). The
    # values are a tuple as (nRows, nCols).
    pageLayoutDict = {
        1: (1, 1),
        2: (2, 1),
        4: (2, 2)}

    # Determine the number of pages that are needed to make the number
    # of cards requested.
    nPages = ceil(nCards / nCardsPerPage)

    # Get the number of rows and columns in each card
    nRows = int(cardSize[0])
    nCols = int(cardSize[-1])

    # Define keys to iterate over while populating each column of each
    # card.
    if scatter:
        # If values are scattered over entire card, the values to use
        # will be in a single list with their dict key being None.
        colIter = (None,) * nCols
    else:
        # Iterate over each column
        colIter = valuesDict.keys()

    #pdb.set_trace()
    with PdfPages(outFile) as pdf:
        # Loop for each page
        for p in range(nPages):
            # Create figure for this page
            (nAxRows, nAxCols) = pageLayoutDict[nCardsPerPage]
            fig, axArr = plt.subplots(nAxRows, nAxCols, squeeze=False)
            fig.set_size_inches(8.5, 11)
            rend = get_renderer(fig)
            # Loop for each card on the current page
            for ax in axArr.flat:
                # Create values for current card
                useColumnLabels = False
                if columnLabelList is not None:
                    useColumnLabels = True
                # Shuffle the card values
                shuffleDict = deepcopy(valuesDict)
                if scatter:
                    # Shuffle all values from all columns together
                    if None in shuffleDict:
                        # All card values are already in a single list
                        shuffle(shuffleDict[None])
                    else:
                        # Card values are in separate columns. Put them
                        # into a single list. The None key contains all
                        # values in a single list.
                        shuffleDict[None] = []
                        for k in valuesDict:
                            shuffleDict[None].extend(valuesDict[k])
                        shuffle(shuffleDict[None])
                else:
                    # Shuffle values within their columns. valuesDict
                    # must contain column information.
                    for k in valuesDict:
                        shuffle(shuffleDict[k])
                # Loop to populate each card column
                cardTextDict = OrderedDict()
                for iCol,colName in enumerate(colIter):
                    if useColumnLabels:
                        cardTextDict[iCol] = [columnLabelList[iCol]]
                    else:
                        cardTextDict[iCol] = []
                    # Make iterator for rows. Use the current column
                    # nRows times.
                    rowIter = (colName,) * nRows
                    # Loop for each row of current column
                    for row in rowIter:
                        cardTextDict[iCol].append(shuffleDict[row].pop())
                # Now need to "transpose" cardTextDict. The values of
                # each key (card column) of cardTextDict are all the
                # values for that column. The table function needs the
                # values of all columns for each row.
                cardTextList = []
                # Loop for each row of list (looks how the card is
                # actually printed)
                nRowsPrinted = nRows + 1 if useColumnLabels else nRows
                for iRow in range(nRowsPrinted):
                    # Get the "iRowth" value of each key (column) of
                    # cardTextDict. 
                    cardTextList.append(
                        [cardTextDict[k][iRow] for k in cardTextDict])
                # Card contents have been determined. Check if we are
                # assigning a free space
                if useFreeSpace:
                    if (nRows % 2) != 0:
                        # Odd number of rows, assign middle row
                        iRowFree = floor(nRows / 2)
                    else:
                        # Even number of rows, randomly assign free space
                        iRowFree = randint(0, nRows-1)
                    if useColumnLabels:
                        iRowFree += 1
                    if (nCols % 2) != 0:
                        # Odd number of columns, assign middle column
                        iColFree = floor(nCols / 2)
                    else:
                        # Even number of columns, randomly assign free
                        # space
                        iColFree = randint(0, nCols-1)
                    cardTextList[iRowFree][iColFree] = '\u2606' # star
                # Create the table on the page and format it
                table = ax.table(cellText=cardTextList,
                    cellLoc='center', loc='upper right')
                ax.set_axis_off()
                if cardTitle is not None:
                    ax.set_title(cardTitle, fontsize=20)
                if nCardsPerPage == 1:
                    table.scale(1, 4)
                elif nCardsPerPage == 2:
                    table.scale(1, 3)
                else:
                    table.scale(1, 2)
                table.auto_set_font_size(False)
                table.set_fontsize(16)
                # For the column label row, only draw the bottom edge
                # of each cell
                if useColumnLabels:
                    for iCol in range(nCols):
                        table[0,iCol].visible_edges = 'B'
                # Formatting applied to every cell. Make the font size
                # as large as possible without going out of the cell
                # boundaries. For multiline card space values, don't
                # auto set the font size, but assign a smaller font
                # size.
                for cell in table.get_celld().values():
                    if '\n' in cell.get_text().get_text():
                        cell.set_fontsize(multiLineFontSize)
                    else:
                        cell.PAD = 0.0005
                        cell.auto_set_font_size(rend)
            
            # All cards on the current page have been made. Adjust card
            # spacing on page.
            fig.set_tight_layout({'rect': (0.05, 0, 0.95, 0.95)})
            plt.subplots_adjust(wspace=0.05, hspace=0.1)
            pdf.savefig()
            plt.close()
        # end of function make_cards


def main():
    '''
    Main function.
    '''
    # Define command-line help message
    descriptionMsg = 'Script to generate bingo cards.'
    helpDict = {
        'cardFile': 'Name of output PDF file of generated bingo cards. ' \
            + f'The default name is: {DEFAULTS["out file"]}.',
        'cardSize': 'Number of rows and columns of each card. Valid ' \
            + 'values are "3x3", "4x4", and "5x5". The default value ' \
            + f'is: {DEFAULTS["card size"]}.',
        'cardsPerPage': 'Number of bingo cards per printed page. ' \
            + 'Valid values are 1, 2, and 4. The default value is ' \
            + f'{DEFAULTS["cards per page"]}.',
        'cardTitle': 'Title on each bingo card',
        'columnLabels': 'Comma-delimited string where value(s) between ' \
            + 'commas are used as the card column labels. The default ' \
            + f'value is: {DEFAULTS["column labels"]}',
        'columnLabelsOff': 'Option to not print column labels on card',
        'multiLineFontSize': 'Font size of text that is spread out on ' \
            + 'multiple lines of a card space. Text on a single line ' \
            + 'is automatically sized to fit in the card spaces, but ' \
            + 'text on multiple lines is not. The default font size ' \
            + f'is {DEFAULTS["multiLineFontSize"]}.',
        'nCards': 'Number of cards to generate',
        'noFree': 'Option to not make the center space of each card a ' \
            + 'free space. If using card size of "4x4", the free space ' \
            + 'is randomly chosen.',
        'scatter': 'Option to scatter card values around the card. The ' \
            + 'default is to randomize values within each column.',
        'valueFile': 'Path to file containing values to use for the ' \
            + 'bingo card spaces. The format can be one card space ' \
            + 'value per line or to use specific values for specific ' \
            + 'columns, each line is: column name::space value, ' \
            + 'such as: B::1, B::2, ..., N::74, N::75'}

    # Parse command line input
    parser = argparse.ArgumentParser(description=descriptionMsg)
    parser.add_argument('nCards', type=int, help=helpDict['nCards'])
    parser.add_argument('--card-file', default=DEFAULTS['out file'],
        help=helpDict['cardFile'])
    parser.add_argument('--card-size', choices=['3x3','4x4','5x5'],
        default=DEFAULTS['card size'], help=helpDict['cardSize'])
    parser.add_argument('--cards-per-page', type=int, choices=[1,2,4],
        default=DEFAULTS['cards per page'], help=helpDict['cardsPerPage'])
    parser.add_argument('--card-title', help=helpDict['cardTitle'])
    colLabelGrp = parser.add_mutually_exclusive_group()
    colLabelGrp.add_argument('--column-labels',
        default=DEFAULTS['column labels'], help=helpDict['columnLabels'])
    colLabelGrp.add_argument('--column-labels-off', action='store_true',
        help=helpDict['columnLabelsOff'])
    parser.add_argument('--multiline-font-size', type=int,
        default=DEFAULTS['multiLineFontSize'],
        help=helpDict['multiLineFontSize'])
    parser.add_argument('--no-free', action='store_true',
       help=helpDict['noFree'])
    parser.add_argument('--scatter', action='store_true',
        help=helpDict['scatter'])
    parser.add_argument('--value-file', help=helpDict['valueFile'])
    args = parser.parse_args()
    
    # Make a list of column labels
    nCols = int(args.card_size[-1])
    if args.column_labels_off:
        colList = None
    else:
        colList = args.column_labels.split(',')
        # If number of columns != number of column labels, then don't
        # use column labels.
        if nCols != len(colList):
            colList = None
    
    # Assign dict containing card space values. The columns are keys
    # and the values are a list containing the values for that column.
    # If columns are not used, there is a single key of None and the
    # value is a list containing all the possible card space values.
    if args.value_file is None:
        # Space values are for a standard bingo card
        spaceValuesDict = OrderedDict([
            ('B', [str(x) for x in range(1, 16)]),
            ('I', [str(x) for x in range(16, 31)]),
            ('N', [str(x) for x in range(31, 46)]),
            ('G', [str(x) for x in range(46, 61)]),
            ('O', [str(x) for x in range(61, 76)])])
    else:
        # Space values are read from a file
        with open(args.value_file) as fin:
            spaceLinesList = fin.readlines()
        if not spaceLinesList:
            errMsg = f'No space values were found in {args.value_file}'
            raise ValueError(errMsg)
        # Test to see if columns are included in the file data
        useLabels = False
        if len(spaceLinesList[0].split('::')) > 1:
            useLabels = True
        if useLabels:
            # Reading labels from each line of file data
            spaceValuesDict = OrderedDict()
            for line in spaceLinesList:
                lineSp = line.split('::')
                label = lineSp[0]
                value = lineSp[1].rstrip().replace('\\n', '\n')
                if label not in spaceValuesDict:
                    spaceValuesDict[label] = [value]
                else:
                    spaceValuesDict[label].append(value)
        else:
            # Not using labels
            spaceValuesDict = {None: []}
            for line in spaceLinesList:
                spaceValuesDict[None].append(
                    line.rstrip().replace('\\n', '\n'))

    # Check that the number of keys in spaceValuesDict matches the
    # number of card columns.
    if None not in spaceValuesDict:
        if len(spaceValuesDict) > nCols:
            # Only use the first nCols keys of spaceValuesDict
            keyDeleteList = []
            for i,k in enumerate(spaceValuesDict):
                if (i+1) > nCols:
                    keyDeleteList.append(k)
            while keyDeleteList:
                del spaceValuesDict[keyDeleteList.pop()]
        elif len(spaceValuesDict) < nCols:
            errMsg = 'ERROR: The number of columns labels is less ' \
                + 'than the number of columns on the cards. Please ' \
                + 'make the number of column labels equal to the ' \
                + 'number of card columns.'
            print(errMsg)
            return
    
    # Make cards
    make_cards(spaceValuesDict, args.nCards, cardSize=args.card_size,
        cardTitle=args.card_title, columnLabelList=colList,
        multiLineFontSize=args.multiline_font_size,
        nCardsPerPage=args.cards_per_page, outFile=args.card_file,
        scatter=args.scatter, useFreeSpace=(not args.no_free))
    # end of function main


if __name__ == '__main__':
    main()
