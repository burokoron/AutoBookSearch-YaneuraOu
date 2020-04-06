#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
肥大化してしまった定跡を減らす
"""

import argparse
import shogi
from tqdm import tqdm



def load_yaneura_book(fpath):
    """
    やねうら定跡を読み込む
    """

    book = {}
    with open(fpath) as file:
        data = file.readline()
        data = file.readline()
        data = data.replace('\n', '')
        data = data.replace('sfen ', '')
        while data != '':
            data = data.split(' ')
            turn = data[3]
            data = data[0] + " " + data[1] + " " + data[2]

            move_list = {}
            move = file.readline()
            move = move.replace('\n', '')
            while not 'sfen' in move:
                move = move.split()
                move_list[move[0]] = {}
                move_list[move[0]]['move'] = move[1]
                move_list[move[0]]['value'] = int(move[2])
                move_list[move[0]]['depth'] = int(move[3])

                move = file.readline()
                move = move.replace('\n', '')
                if move == '':
                    break

            book[data] = {}
            book[data]['moves'] = move_list
            book[data]['turn'] = int(turn)

            data = move.replace('sfen ', '')

    return book


def worst_search(theme_file, book, k, player):
    """
    最悪応手上位ratio%の末端局面を削除する
    """

    with open(theme_file) as file:
        theme_list = file.read()
        theme_list = theme_list.split('\n')
        if '' in theme_list:
            theme_list.remove('')

    for theme in tqdm(theme_list, desc='theme'):
        bar = tqdm(total=k, desc='delete')
        delete_nums = 0
        while delete_nums < k:
            # プログレスバーの更新
            bar.update(1)

            same_pos = set()
            preview = ['startpos moves', 0]

            # 課題局面まで動かす
            board = shogi.Board()
            sfen = board.sfen().split(' ')
            sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
            same_pos.add(sfen)
            move_list = theme.split(' ')
            if '' in move_list:
                move_list.remove('')
            if len(move_list) != 2:
                for move in move_list[2:]:
                    board.push_usi(move)
                    preview[0] += ' ' + move
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                    if sfen in same_pos:
                        break
                    same_pos.add(sfen)

            # 最悪応手探索
            while sfen in book:
                move_list = {}
                for move in book[sfen]['moves']:
                    if abs(book[sfen]['moves'][move]['value']) > 50000:
                        continue
                    move_list[move] = book[sfen]['moves'][move]['value']
                if move_list == {}:
                    break
                if player == 'all' or \
                    (player == 'black' and book[sfen]['turn']%2 != 0) or \
                    (player == 'white' and book[sfen]['turn']%2 == 0):
                    move = min(move_list, key=move_list.get)
                    board.push_usi(move)
                    preview[0] += ' ' + move
                    preview[1] = min(move_list.values())
                else:
                    move = max(move_list, key=move_list.get)
                    board.push_usi(move)
                    preview[0] += ' ' + move
                    preview[1] = max(move_list.values())
                sfen = board.sfen().split(' ')
                sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                if sfen in same_pos:
                    break
                same_pos.add(sfen)


            # 最善応手の末端局面を削除する
            if int(board.sfen().split(' ')[-1]) == 1:
                break
            board.pop()
            sfen = board.sfen().split(' ')
            sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
            delete_nums += 1
            move_list = {}
            for move in book[sfen]['moves']:
                move_list[move] = book[sfen]['moves'][move]['value']
            if len(move_list) == 1:
                book.pop(sfen, None)
            else:
                move = min(move_list, key=move_list.get)
                book[sfen]['moves'].pop(move, None)


    return book



def main(args):
    '''
    メイン関数
    '''

    # 定跡を読み込む
    yane_book = load_yaneura_book(args.yanebook)
    tera_book = load_yaneura_book(args.terabook)

    # テラショック定跡の登録手数
    move_nums = 0
    for pos in tera_book:
        move_nums += len(tera_book[pos]['moves'])

    # 最悪応手の末端局面を削除
    tera_book = worst_search(args.theme, tera_book,
                             int(move_nums*args.ratio),
                             args.turn)


    print(f'{len(yane_book)-len(tera_book)} positions, ', end='')
    print(f'{100-len(tera_book)/len(yane_book)*100:.2f}% removed.')
    # 不要な局面を通常のやねうら定跡から削除
    delete_list = []
    for sfen in yane_book:
        if sfen not in tera_book:
            delete_list.append(sfen)
    for sfen in delete_list:
        yane_book.pop(sfen, None)

    # 削減した定跡を出力
    with open(f'{args.output}', 'w') as file:
        file.write('#YANEURAOU-DB2016 1.00\n')

        for sfen in sorted(yane_book.keys()):
            file.write('sfen %s %d\n' %(sfen,
                                        yane_book[sfen]['turn']))
            for move in yane_book[sfen]['moves']:
                file.write('%s %s %d %d %d\n' %(move,
                                                yane_book[sfen]['moves'][move]['move'],
                                                yane_book[sfen]['moves'][move]['value'],
                                                yane_book[sfen]['moves'][move]['depth'],
                                                1))


if __name__ == '__main__':
    # 引数の定義
    parser = argparse.ArgumentParser(description='reducing book')

    parser.add_argument('-yane', '--yanebook', required=True) # 通常のやねうら定跡のファイルパス
    parser.add_argument('-tera', '--terabook', required=True) # テラショック定跡のファイルパス
    parser.add_argument('-o', '--output', required=True) # 削減したやねうら定跡のファイルパス
    parser.add_argument('-theme', '--theme', required=True) # 課題局面までの手順が書かれたファイルのパス
    parser.add_argument('-r', '--ratio', type=float, required=True) # 定跡の削減率
    parser.add_argument('-turn', '--turn', type=str, default='all') # 削減対象の手番

    args = parser.parse_args()

    main(args)
