#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定跡探索を行う
"""

import os
import sys
import subprocess as sp
import numpy as np
import shogi


class BestPVSearch:
    """
    定跡探索を行うクラス
    """

    def __init__(self, options):
        self.options = options
        self.yaneura_book = {}
        self.terashock_book = {}
        self.multi_pv = int(options['Search']['MinMultiPV'])
        self.black_resign = None
        self.white_resign = None
        self.book_count = 0
        self.shogi_pos = {'A1': shogi.A1, 'A2': shogi.A2, 'A3': shogi.A3, 'A4': shogi.A4, 'A5': shogi.A5, 'A6': shogi.A6, 'A7': shogi.A7, 'A8': shogi.A8, 'A9': shogi.A9,
                          'B1': shogi.B1, 'B2': shogi.B2, 'B3': shogi.B3, 'B4': shogi.B4, 'B5': shogi.B5, 'B6': shogi.B6, 'B7': shogi.B7, 'B8': shogi.B8, 'B9': shogi.B9,
                          'C1': shogi.C1, 'C2': shogi.C2, 'C3': shogi.C3, 'C4': shogi.C4, 'C5': shogi.C5, 'C6': shogi.C6, 'C7': shogi.C7, 'C8': shogi.C8, 'C9': shogi.C9,
                          'D1': shogi.D1, 'D2': shogi.D2, 'D3': shogi.D3, 'D4': shogi.D4, 'D5': shogi.D5, 'D6': shogi.D6, 'D7': shogi.D7, 'D8': shogi.D8, 'D9': shogi.D9,
                          'E1': shogi.E1, 'E2': shogi.E2, 'E3': shogi.E3, 'E4': shogi.E4, 'E5': shogi.E5, 'E6': shogi.E6, 'E7': shogi.E7, 'E8': shogi.E8, 'E9': shogi.E9,
                          'F1': shogi.F1, 'F2': shogi.F2, 'F3': shogi.F3, 'F4': shogi.F4, 'F5': shogi.F5, 'F6': shogi.F6, 'F7': shogi.F7, 'F8': shogi.F8, 'F9': shogi.F9,
                          'G1': shogi.G1, 'G2': shogi.G2, 'G3': shogi.G3, 'G4': shogi.G4, 'G5': shogi.G5, 'G6': shogi.G6, 'G7': shogi.G7, 'G8': shogi.G8, 'G9': shogi.G9,
                          'H1': shogi.H1, 'H2': shogi.H2, 'H3': shogi.H3, 'H4': shogi.H4, 'H5': shogi.H5, 'H6': shogi.H6, 'H7': shogi.H7, 'H8': shogi.H8, 'H9': shogi.H9,
                          'I1': shogi.I1, 'I2': shogi.I2, 'I3': shogi.I3, 'I4': shogi.I4, 'I5': shogi.I5, 'I6': shogi.I6, 'I7': shogi.I7, 'I8': shogi.I8, 'I9': shogi.I9,}



    @staticmethod
    def _load_yaneura_book(fpath):
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



    def make_theme_book(self):
        """
        課題局面までの手順を定跡化する
        """

        # やねうら王定跡に登録されている局面の探索深さを調べる
        with open(self.options['Search']['YaneuraDBFile']) as file:
            max_depth = 0
            data = file.readline()
            data = file.readline()
            data = data.replace('\n', '')
            data = data.replace('sfen ', '')
            while data != '':
                data = data.split(' ')
                data = data[0] + " " + data[1] + " " + data[2]

                move = file.readline()
                move = move.replace('\n', '')
                while not 'sfen' in move:
                    max_depth = max(max_depth, int(move.split(' ')[3]))
                    move = file.readline()
                    move = move.replace('\n', '')
                    if move == '':
                        break

                data = move.replace('sfen ', '')

        # 定跡の探索深さの最大値よりも今回の探索深さが小さいときはエラー
        if max_depth > int(self.options['YaneuraOu']['Depth']):
            print('Depth should be set to %d or more.' %(max_depth))
            sys.exit(1)


        # 課題局面までの手順を探索し，定跡化作成する
        with open(self.options['Search']['CommandFile'], 'w') as file:
            file.write('EvalDir %s\n' %(self.options['YaneuraOu']['EvalDir']))
            file.write('BookDir %s\n' %(self.options['YaneuraOu']['BookDir']))
            file.write('Hash %s\n' %(self.options['YaneuraOu']['Hash']))
            file.write('Threads %s\n' %(self.options['YaneuraOu']['Threads']))
            file.write('MultiPV 1\n')
            file.write('makebook think %s %s '
                       %(self.options['Search']['ThemeSfenFile'],
                         self.options['Search']['YaneuraDBFile']))
            file.write('startmoves 1 moves %s depth %s nodes %s\n'
                       %(self.options['Search']['MaxMoves'],
                         self.options['YaneuraOu']['Depth'],
                         self.options['YaneuraOu']['Nodes']))
            file.write('makebook build_tree %s %s '
                       %(self.options['Search']['YaneuraDBFile'],
                         self.options['Search']['TeraShockDBFile']))
            file.write('black_contempt %d white_contempt %d\n'
                       %(int(self.options['YaneuraOu']['BlackContempt'])*-1,
                         int(self.options['YaneuraOu']['WhiteContempt'])*-1))
            file.write('quit\n')

        cmd = (self.options['YaneuraOu']['EngineFile'] + " file "
               + self.options['Search']['CommandFile'])
        sp.call(cmd.split())



    def bulid_terashock_build(self):
        """
        やねうら定跡をテラショック定跡に変換する
        """
        with open(self.options['Search']['CommandFile'], 'w') as file:
            file.write('EvalDir %s\n' %(self.options['YaneuraOu']['EvalDir']))
            file.write('BookDir %s\n' %(self.options['YaneuraOu']['BookDir']))
            file.write('Hash %s\n' %(self.options['YaneuraOu']['Hash']))
            file.write('Threads %s\n' %(self.options['YaneuraOu']['Threads']))
            file.write('MultiPV 1\n')
            file.write('makebook build_tree %s %s '
                       %(self.options['Search']['YaneuraDBFile'],
                         self.options['Search']['TeraShockDBFile']))
            file.write('black_contempt %d white_contempt %d\n'
                       %(int(self.options['YaneuraOu']['BlackContempt'])*-1,
                         int(self.options['YaneuraOu']['WhiteContempt'])*-1))
            file.write('quit\n')

        cmd = (self.options['YaneuraOu']['EngineFile'] + " file "
               + self.options['Search']['CommandFile'])
        sp.call(cmd.split())



    @staticmethod
    def _pv_search(theme_file, book, k, correction):
        """
        最善応手上位(課題局面数×k)手を調べる
        """

        with open(theme_file) as file:
            theme_list = file.read()
            theme_list = theme_list.split('\n')
            if '' in theme_list:
                theme_list.remove('')

        for theme in theme_list:
            pv_list = []
            for i in range(k):
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
                        else:
                            same_pos.add(sfen)

                # 最善応手探索
                while sfen in book:
                    move_list = {}
                    for move in book[sfen]['moves']:
                        if i == 0:
                            move_list[move] = book[sfen]['moves'][move]['value']
                        else:
                            move_list[move] = book[sfen]['moves'][move]['value'] \
                                - (np.log2(book[sfen]['moves'][move]['depth'] + 1)
                                   * correction)
                    move = max(move_list, key=move_list.get)
                    board.push_usi(move)
                    preview[0] += ' ' + move
                    preview[1] = max(move_list.values())
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                    if sfen in same_pos:
                        break
                    else:
                        same_pos.add(sfen)

                pv_list.append(preview)

                # 最善応手の末端局面の評価値を悪くする
                if int(board.sfen().split(' ')[-1]) == 1:
                    break
                board.pop()
                sfen = board.sfen().split(' ')
                sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                move_list = {}
                for move in book[sfen]['moves']:
                    move_list[move] = book[sfen]['moves'][move]['value']
                move = max(move_list, key=move_list.get)
                book[sfen]['moves'][move]['value'] -= 100000
                book[sfen]['moves'][move]['value'] -= 100000
                max_value = max(move_list.values())
                if int(board.sfen().split(' ')[-1]) == 1:
                    break

                # 評価値の伝搬
                while True:
                    board.pop()
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                    move_list = {}
                    for move in book[sfen]['moves']:
                        move_list[move] = book[sfen]['moves'][move]['value']
                    move = max(move_list, key=move_list.get)
                    book[sfen]['moves'][move]['value'] = -max_value
                    max_value = max(move_list.values())
                    if int(board.sfen().split(' ')[-1]) == 1:
                        break


        return pv_list



    def _update_multipv(self, pv_list):
        """
        MultiPVの更新
        投了評価値未満ならMultiPVを2倍にする
        投了評価値以上ならMultiPVを最小値にする
        """

        self.black_resign = None
        self.white_resign = None
        if self.options.getboolean('Search', 'AutoMultiPV'):
            for preview in pv_list:
                if len(preview[0].split(' ')) % 2 == 0:
                    if preview[1] > int(
                            self.options['Search']['WhiteResignValue']):
                        self.white_resign = False
                    elif self.white_resign is None:
                        self.white_resign = True
                else:
                    if preview[1] > int(
                            self.options['Search']['BlackResignValue']):
                        self.black_resign = False
                    elif self.black_resign is None:
                        self.black_resign = True

        if self.black_resign or self.white_resign:
            self.multi_pv = min(int(self.options['Search']['MaxMultiPV']),
                                self.multi_pv*2)
        else:
            self.multi_pv = int(self.options['Search']['MinMultiPV'])



    @staticmethod
    def _difference_book_build(yaneura_book, terashock_book, pv_search_file,
                               black_contempt, white_contempt,
                               terashock_book_file):
        """
        テラショック定跡の差分更新を行う
        """

        with open(pv_search_file) as file:
            theme_list = file.read()
            theme_list = theme_list.split('\n')
            if '' in theme_list:
                theme_list.remove('')


        for theme in theme_list:
            same_pos = set()
            draw = False

            # 課題局面まで動かす
            board = shogi.Board()
            sfen = board.sfen().split(' ')
            sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
            # テラショック定跡に存在しない指し手があったらテラショック定跡に追加する
            if sfen in terashock_book:
                for _move in yaneura_book[sfen]['moves']:
                    if _move not in terashock_book[sfen]['moves']:
                        terashock_book[sfen]['moves'][_move] = yaneura_book[sfen]['moves'][_move]
                        terashock_book[sfen]['moves'][_move]['depth'] = 0
            same_pos.add(sfen)
            move_list = theme.split(' ')
            if '' in move_list:
                move_list.remove('')
            if len(move_list) != 2:
                for move in move_list[2:]:
                    board.push_usi(move)
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                    if sfen in same_pos:
                        draw = True
                        break
                    else:
                        same_pos.add(sfen)
                    # テラショック定跡に存在しない指し手があったらテラショック定跡に追加する
                    if sfen in terashock_book:
                        for _move in yaneura_book[sfen]['moves']:
                            if _move not in terashock_book[sfen]['moves']:
                                terashock_book[sfen]['moves'][_move] = \
                                    yaneura_book[sfen]['moves'][_move]
                                terashock_book[sfen]['moves'][_move]['depth'] = 0

            # テラショック定跡に局面を追加
            sfen = board.sfen().split(' ')
            turn = int(sfen[3])
            sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
            if sfen not in terashock_book and sfen in yaneura_book:
                terashock_book[sfen] = yaneura_book[sfen]
                for move in terashock_book[sfen]['moves']:
                    terashock_book[sfen]['moves'][move]['depth'] = 0
            elif sfen in terashock_book and sfen in yaneura_book:
                for move in yaneura_book[sfen]['moves']:
                    if move not in terashock_book[sfen]['moves']:
                        terashock_book[sfen]['moves'][move] = \
                            yaneura_book[sfen]['moves'][move]
                        terashock_book[sfen]['moves'][move]['depth'] = 0
            else:
                board.pop()
                sfen = board.sfen().split(' ')
                turn = int(sfen[3])
                sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]

            # 末端局面の評価値を計算する
            if draw is True:
                if turn%2 != 0:
                    max_value = black_contempt
                else:
                    max_value = white_contempt
            else:
                move_list = {}
                for move in terashock_book[sfen]['moves']:
                    move_list[move] = terashock_book[sfen]['moves'][move]['value']
                max_value = max(move_list.values())

            if int(board.sfen().split(' ')[-1]) == 1:
                break

            # 評価値の伝搬
            while True:
                move = str(board.pop())
                sfen = board.sfen().split(' ')
                turn = int(sfen[3])
                sfen = sfen[0] +" " + sfen[1] + " " + sfen[2]
                # 千日手なら千日手評価値にする
                if draw is True:
                    if turn%2 != 0 and max_value == white_contempt:
                        terashock_book[sfen]['moves'][move]['value'] = black_contempt
                    elif max_value == black_contempt:
                        terashock_book[sfen]['moves'][move]['value'] = white_contempt
                    else:
                        draw = False
                else:
                    terashock_book[sfen]['moves'][move]['value'] = -max_value
                # depthを調べる
                board.push_usi(move)
                next_sfen = board.sfen().split(' ')
                next_sfen = next_sfen[0] +" " + next_sfen[1] + " " + next_sfen[2]
                if next_sfen in terashock_book:
                    next_move_list = {}
                    for next_move in terashock_book[next_sfen]['moves']:
                        next_move_list[next_move] = \
                            terashock_book[next_sfen]['moves'][next_move]['value']
                    next_move = max(next_move_list, key=next_move_list.get)
                    terashock_book[sfen]['moves'][move]['depth'] = \
                        terashock_book[next_sfen]['moves'][next_move]['depth'] + 1
                board.pop()

                move_list = {}
                for move in terashock_book[sfen]['moves']:
                    move_list[move] = terashock_book[sfen]['moves'][move]['value']
                max_value = max(move_list.values())

                if int(board.sfen().split(' ')[-1]) == 1:
                    break


        # テラショック定跡をファイルに書き込む
        with open(terashock_book_file, 'w') as file:
            file.write('#YANEURAOU-DB2016 1.00\n')

            for sfen in sorted(terashock_book.keys()):
                file.write('sfen %s %d\n' %(sfen,
                                            terashock_book[sfen]['turn']))
                for move in terashock_book[sfen]['moves']:
                    file.write('%s %s %d %d %d\n' %(move,
                                                    terashock_book[sfen]['moves'][move]['move'],
                                                    terashock_book[sfen]['moves'][move]['value'],
                                                    terashock_book[sfen]['moves'][move]['depth'],
                                                    1))



    def _forbidden_book(self, book, book_fpath, forbidden_fpath):
        # 禁止条件ファイルを読み込む
        forbidden_pos = {}
        with open(forbidden_fpath, 'r') as file:
            data = file.readline()
            while data != '':
                data = data.split(' ')
                forbidden_pos[data[2]] = {'start': int(data[0]),
                                          'end': int(data[1]),
                                          'pos': data[3:]}
                data = file.readline()

        # 定跡の評価値を更新し、ファイルに書き込む
        with open(book_fpath, 'w') as file:
            file.write('#YANEURAOU-DB2016 1.00\n')

            for sfen in sorted(book.keys()):
                board = shogi.Board(f'{sfen} {book[sfen]["turn"]}')
                flag = False
                for piece in forbidden_pos:
                    if forbidden_pos[piece]['start'] <= book[sfen]['turn'] <= forbidden_pos[piece]['end']:
                        for pos in forbidden_pos[piece]['pos']:
                            if str(board.piece_at(self.shogi_pos[pos])) == piece:
                                flag = True
                file.write('sfen %s %d\n' %(sfen,
                                            book[sfen]['turn']))
                if flag:
                    for move in book[sfen]['moves']:
                        if book[sfen]['turn'] %2 == 0:
                            book[sfen]['moves'][move]['value'] = 10000
                        else:
                            book[sfen]['moves'][move]['value'] = -10000
                        file.write('%s %s %d %d %d\n' %(move,
                                                        book[sfen]['moves'][move]['move'],
                                                        book[sfen]['moves'][move]['value'],
                                                        book[sfen]['moves'][move]['depth'],
                                                        1))
                else:
                    for move in book[sfen]['moves']:
                        file.write('%s %s %d %d %d\n' %(move,
                                                        book[sfen]['moves'][move]['move'],
                                                        book[sfen]['moves'][move]['value'],
                                                        book[sfen]['moves'][move]['depth'],
                                                        1))


        return book




    def search(self):
        """
        登録済み定跡を用いて課題局面からの最善応手上位N手を調べる
        """

        # 定跡データベース
        self.yaneura_book = self._load_yaneura_book(
            self.options['Search']['YaneuraDBFile'])
        self.yaneura_book = self._forbidden_book(
            self.yaneura_book, self.options['Search']['YaneuraDBFile'],
            self.options['Search']['ForbiddenFile'])
        self.terashock_book = self._load_yaneura_book(
            self.options['Search']['TeraShockDBFile'])
        self.terashock_book = self._forbidden_book(
            self.terashock_book, self.options['Search']['TeraShockDBFile'],
            self.options['Search']['ForbiddenFile'])

        # 定跡登録数が増えてなければ探索を終了する
        book_count = len(self.yaneura_book)
        if (self.book_count > book_count
                and self.multi_pv == int(
                    self.options['Search']['MaxMultiPV'])):
            if self.black_resign:
                print('White Win!!')
            elif self.white_resign:
                print('Black Win!!')
            else:
                print('Draw!!')
            sys.exit()
        elif self.book_count == book_count:
            self.book_count += 1
        else:
            self.book_count = book_count


        # 最善応手群の探索
        k = 2 # 探索幅拡張係数

        pv_list = self._pv_search(self.options['Search']['ThemeSfenFile'],
                                  self.terashock_book,
                                  int(int(
                                      self.options['YaneuraOu']['Threads'])
                                      * k),
                                  int(self.options['Search']['CorrectionValue']))

        # 最善応手群をファイルに書き込む
        with open(self.options['Search']['BestPVFile'], 'w') as file:
            for preview in pv_list:
                file.write('%s\n' %(preview[0]))

        # 'AutoMultiPV = yes'ならMultiPVを自動調整する
        self._update_multipv(pv_list)


        # 局面を探索する
        self.make_cmd()
        cmd = (self.options['YaneuraOu']['EngineFile'] + " file "
               + self.options['Search']['CommandFile'])
        sp.call(cmd.split())


        # テラショック定跡の差分ビルド
        self.yaneura_book = self._load_yaneura_book(
            self.options['Search']['YaneuraDBFile'])
        self.terashock_book = self._load_yaneura_book(
            self.options['Search']['TeraShockDBFile'])

        self._difference_book_build(self.yaneura_book, self.terashock_book,
                                    self.options['Search']['BestPVFile'],
                                    int(self.options['YaneuraOu']['BlackContempt']),
                                    int(self.options['YaneuraOu']['WhiteContempt']),
                                    self.options['Search']['TeraShockDBFile'])



    def make_cmd(self):
        """
        やねうら王へのコマンドを生成する
        """

        with open('none.sfen', 'w') as file:
            pass

        with open(self.options['Search']['CommandFile'], 'w') as file:
            file.write('EvalDir %s\n' %(self.options['YaneuraOu']['EvalDir']))
            file.write('BookDir %s\n' %(self.options['YaneuraOu']['BookDir']))
            file.write('Hash %s\n' %(self.options['YaneuraOu']['Hash']))
            file.write('Threads %s\n' %(self.options['YaneuraOu']['Threads']))
            file.write('MultiPV %d\n' %(self.multi_pv))
            if self.black_resign:
                file.write('makebook think bw %s none.sfen %s '
                           %(self.options['Search']['BestPVFile'],
                             self.options['Search']['YaneuraDBFile']))
            elif self.white_resign:
                file.write('makebook think bw none.sfen %s %s '
                           %(self.options['Search']['BestPVFile'],
                             self.options['Search']['YaneuraDBFile']))
            else:
                file.write('makebook think %s %s '
                           %(self.options['Search']['BestPVFile'],
                             self.options['Search']['YaneuraDBFile']))
            file.write('startmoves 1 moves %s depth %s nodes %s\n'
                       %(self.options['Search']['MaxMoves'],
                         self.options['YaneuraOu']['Depth'],
                         self.options['YaneuraOu']['Nodes']))
            file.write('quit\n')

        os.remove('none.sfen')
