#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定跡探索を行う
"""

import os
import sys
import subprocess as sp
import shogi


class BestPVSearch:
    """
    定跡探索を行うクラス
    """

    def __init__(self, options):
        self.options = options
        self.multi_pv = int(options['Search']['MinMultiPV'])
        self.black_resign = True
        self.white_resign = True
        self.book_count = 0


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
                data = data[0] + data[1] + data[2]

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


        # やねうら王定跡からテラショック定跡を作成する
        with open(self.options['Search']['CommandFile'], 'w') as file:
            file.write('EvalDir %s\n' %(self.options['YaneuraOu']['EvalDir']))
            file.write('BookDir %s\n' %(self.options['YaneuraOu']['BookDir']))
            file.write('Hash %s\n' %(self.options['YaneuraOu']['Hash']))
            file.write('Threads %s\n' %(self.options['YaneuraOu']['Threads']))
            file.write('makebook build_tree %s %s\n'
                       %(self.options['Search']['YaneuraDBFile'],
                         self.options['Search']['TeraShockDBFile']))
            file.write('quit\n')

        cmd = (self.options['YaneuraOu']['EngineFile'] + " file "
               + self.options['Search']['CommandFile'])
        sp.call(cmd.split())


        # 課題局面までの手順を定跡に登録
        print('make theme book')


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
            file.write('makebook build_tree %s %s\n'
                       %(self.options['Search']['YaneuraDBFile'],
                         self.options['Search']['TeraShockDBFile']))
            file.write('quit\n')

        cmd = (self.options['YaneuraOu']['EngineFile'] + " file "
               + self.options['Search']['CommandFile'])
        sp.call(cmd.split())



    def _pv_search(self, theme_file, book, k):
        """
        最善応手上位(課題局面数×k)手を調べる
        """

        with open(theme_file) as file:
            theme_list = file.read()
            theme_list = theme_list.split('\n')
            if '' in theme_list:
                theme_list.remove('')

        all_pv_list = []
        for theme in theme_list:
            pv_list = []
            for _ in range(k):
                same_pos = set()
                preview = ['startpos moves', 0]

                # 課題局面まで動かす
                board = shogi.Board()
                sfen = board.sfen().split(' ')
                sfen = sfen[0] + sfen[1] + sfen[2]
                same_pos.add(sfen)
                move_list = theme.split(' ')
                if '' in move_list:
                    move_list.remove('')
                if len(move_list) != 2:
                    for move in move_list[2:]:
                        board.push_usi(move)
                        preview[0] += ' ' + move
                        sfen = board.sfen().split(' ')
                        sfen = sfen[0] + sfen[1] + sfen[2]
                        if sfen in same_pos:
                            break
                        else:
                            same_pos.add(sfen)

                # 最善応手探索
                while sfen in book:
                    move_list = book[sfen]
                    move = max(move_list, key=move_list.get)
                    board.push_usi(move)
                    preview[0] += ' ' + move
                    preview[1] = max(move_list.values())
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] + sfen[1] + sfen[2]
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
                sfen = sfen[0] + sfen[1] + sfen[2]
                move_list = book[sfen]
                move = max(move_list, key=move_list.get)
                book[sfen][move] -= 100000
                book[sfen][move] -= 100000
                max_value = max(move_list.values())
                if int(board.sfen().split(' ')[-1]) == 1:
                    break

                # 評価値の伝搬
                while True:
                    board.pop()
                    sfen = board.sfen().split(' ')
                    sfen = sfen[0] + sfen[1] + sfen[2]
                    move_list = book[sfen]
                    move = max(move_list, key=move_list.get)
                    book[sfen][move] = -max_value
                    max_value = max(move_list.values())
                    if int(board.sfen().split(' ')[-1]) == 1:
                        break

            all_pv_list += pv_list


        return all_pv_list



    def search(self):
        """
        登録済み定跡を用いて課題局面からの最善応手上位N手を調べる
        """

        # 定跡データベース
        book = {}
        with open(self.options['Search']['TeraShockDBFile']) as file:
            data = file.readline()
            data = file.readline()
            data = data.replace('\n', '')
            data = data.replace('sfen ', '')
            while data != '':
                data = data.split(' ')
                data = data[0] + data[1] + data[2]

                move_list = {}
                move = file.readline()
                move = move.replace('\n', '')
                while not 'sfen' in move:
                    move_list[move.split(' ')[0]] = int(move.split(' ')[2])
                    move = file.readline()
                    move = move.replace('\n', '')
                    if move == '':
                        break

                book[data] = move_list

                data = move.replace('sfen ', '')

        # 定跡登録数が増えてなければ探索を終了する
        book_count = len(book)
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
        k = 1.5 # 探索幅拡張係数

        pv_list = self._pv_search(self.options['Search']['ThemeSfenFile'],
                                  book,
                                  int(int(
                                      self.options['YaneuraOu']['Threads'])
                                      * k))

        # 最善応手群をファイルに書き込む
        with open(self.options['Search']['BestPVFile'], 'w') as file:
            for preview in pv_list:
                file.write('%s\n' %(preview[0]))

        # 'AutoMultiPV = yes'ならMultiPVを自動調整する
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
            file.write('makebook build_tree %s %s\n'
                       %(self.options['Search']['YaneuraDBFile'],
                         self.options['Search']['TeraShockDBFile']))
            file.write('quit\n')

        os.remove('none.sfen')
