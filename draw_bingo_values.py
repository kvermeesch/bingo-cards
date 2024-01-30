'''
Script to draw Bingo numbers to play the game
'''

import argparse
from collections import namedtuple
from random import shuffle

# Define object to hold call (drawn) value column label and bingo card
# space value.
DrawValue_t = namedtuple('DrawValue_t', ['label', 'value'])


def main():
    '''
    Main function
    '''
    # Define command-line help message
    descriptionMsg = 'Script to draw / call Bingo numbers or game ' \
        + 'play values.'
    helpDict = {
        'cardSize': 'Number of rows and columns of each card. Valid ' \
            + 'values are "3x3", "4x4", and "5x5". The default value ' \
            + 'is: 5x5.',
        'ignoreColumn': 'Option to not use the column label (if one ' \
            + 'is used) when displaying the drawn values. This is ' \
            + 'useful if the player bingo cards do not have column ' \
            + 'labels OR the cards were created using the --scatter ' \
            + 'option with make_bingo_cards.py.',
        'valueFile': 'Path to file containing values that correspond ' \
            + 'to spaces of the players\' bingo cards that will be ' \
            + 'spoken by the bingo caller. The format is one bingo ' \
            + 'card space value per line optionally prefixed by a ' \
            + 'column label. Example: 1, 2, ..., 74, 75 OR B::1, B::2, '\
            + '..., N::74, N::75 (if using column labels).'}

    # Parse command line input
    parser = argparse.ArgumentParser(description=descriptionMsg)
    valGrp = parser.add_mutually_exclusive_group()
    valGrp.add_argument('--card-size', choices=['3x3','4x4','5x5'],
        default='5x5', help=helpDict['cardSize'])
    valGrp.add_argument('--value-file', help=helpDict['valueFile'])
    parser.add_argument('--ignore-column', action='store_true',
        help=helpDict['ignoreColumn'])
    args = parser.parse_args()

    sayColumns = not args.ignore_column

    # Assign values to draw from
    if args.value_file is None:
        # Drawn values are for a standard bingo card
        drawValuesDict = {
            'B': [str(x) for x in range(1, 16)],
            'I': [str(x) for x in range(16, 31)],
            'N': [str(x) for x in range(31, 46)],
            'G': [str(x) for x in range(46, 61)],
            'O': [str(x) for x in range(61, 76)]}
        if args.card_size == '3x3':
            # Delete the 'G' and 'O' columns
            del drawValuesDict['G'], drawValuesDict['O']
        elif args.card_size == '4x4':
            # Delete the 'O' column
            del drawValuesDict['O']
    else:
        # Drawn values are read from a file
        with open(args.value_file) as fin:
            drawLinesList = fin.readlines()
        if not drawLinesList:
            errMsg = f'No values were found in {args.value_file}'
            raise ValueError(errMsg)
        # Test to see if columns are included in the file data
        useLabels = False
        if len(drawLinesList[0].split('::')) > 1:
            useLabels = True
        if useLabels:
            # Reading labels from each line of file data
            drawValuesDict = {}
            for line in drawLinesList:
                lineSp = line.split('::')
                label = lineSp[0]
                value = lineSp[1].rstrip().replace('\\n', '\n')
                if label not in drawValuesDict:
                    drawValuesDict[label] = [value]
                else:
                    drawValuesDict[label].append(value)
        else:
            # Not using labels
            drawValuesDict = {None: []}
            for line in drawLinesList:
                drawValuesDict[None].append(
                    line.rstrip().replace('\\n', '\n'))
        
    # Put all values into a single list
    drawValuesList = []
    if None in drawValuesDict:
        # All values are already in a single list and not using column
        # labels.
        for v in drawValuesDict[None]:
            drawValuesList.append(DrawValue_t('', v))
    else:
        for label in drawValuesDict:
            for v in drawValuesDict[label]:
                drawValuesList.append(DrawValue_t(label, v))
        
    # Shuffle the values to draw
    shuffle(drawValuesList)

    # Loop to play game (draw values)
    drawCount = 0
    drawAgain = True
    print('Enter Q or q to quit.')
    while drawValuesList and drawAgain:
        drawCount += 1
        v = drawValuesList.pop()
        if sayColumns:
            print(f'{drawCount}) {v.label} {v.value}')
        else:
            print(f'{drawCount}) {v.value}')
        userInput = input('')
        if userInput.lower() == 'q':
            drawAgain = False
    if (not drawValuesList) and drawAgain:
        # All the values have been drawn, but another draw is requested
        print('All the values have been drawn.')
    # end of function main


if __name__ =='__main__':
    main()
