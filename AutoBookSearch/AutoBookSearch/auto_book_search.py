#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
定跡を自動で効率良く探索する
やねうら王v4.87以上推奨
"""

import os
import sys
import subprocess as sp
import configparser

from lib.best_pv_search import search, make_cmd, make_theme_book



def main():
    """
    定跡を自動で探索する
    """
    # 作業ディレクトリを自身のファイルのディレクトリに変更
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    # 設定ファイルのロード
    options = configparser.ConfigParser()
    options.optionxform = str
    options.read('options.ini', encoding='utf-8')


    # 課題局面までの手順を定跡として作成する
    make_theme_book(options)


    # 定跡探索
    multi_pv = int(options['Search']['MinMultiPV'])
    for i in range(int(options['Search']['MaxLoops'])):
        print("loop %d/%d" %(i+1, int(options['Search']['MaxLoops'])))
        multi_pv, black_resign, white_resign = search(options, multi_pv)
        make_cmd(options, multi_pv, black_resign, white_resign)
        cmd = (options['YaneuraOu']['EngineFile'] + " file "
               + options['Search']['CommandFile'])
        sp.call(cmd.split())


if __name__ == '__main__':
    main()
