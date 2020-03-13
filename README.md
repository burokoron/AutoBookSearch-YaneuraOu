# AutoBookSearch-YaneuraOu
A tool for the book generation using YaneuraOu.

�����\�t�g�u[��˂��牤](https://github.com/yaneurao/YaneuraOu)�v���g���ē���ǖʂ����Ղ������T������c�[��

### ����
- ���L���ȋǖʂ���L���ȋǖʂɂ����Ă����菇�������I�ɒT���ł���
- ����̋�̋֎~�ʒu��ݒ肷�邱�ƂŔC�ӂ̐�^�T�����ł���
  - ��F10�`20��ڂɔ�Ԃ�1�`4�؂ɂ��邱�Ƃ��֎~���邱�ƂŖ������U���Ԃɂ���

### ����ۏ؊�
- YaneuraOu�Fv4.86
- python�F3.7.4
- numpy�F1.16.5
- python-shogi�F1.0.8

### �g����
options.ini�Ƀp�����[�^��K�؂ɐݒ肵auto_book_search.py�����s����B

#### options.ini
- YaneuraOu
  - EngineFile�F��˂��牤�̎��s�t�@�C���̃p�X
  - EvalDir�F�]���֐�������t�H���_�̃p�X
  - BookDir:��Ճt�@�C���̃p�X
  - Hash�F�u���\�̃T�C�Y
  - Threads�F�X���b�h��
  - Depth�F�T���[��
  - Nodes�F1�ǖʂɂ�����ő�T���ǖʐ�
  - BlackContempt�F���̐����]���l(���ڐ�)
  - WhiteContempt�F���̐����]���l(���ڐ�)
- Search
  - ThemeSfenFile�F�ۑ�ǖʂ܂ł̎菇���L�q����sfen�t�@�C��
    - ��Fstartpos moves 7g7f
    - �����s�w���(������������̂Ŕ񐄏�)
  - ForbiddenFile�F��̈ʒu�̋֎~�������L�q�����t�@�C��
    - ��F10 20 R A1 A2 A3 A4 B1 B2 B3 B4 C1 C2 C3 C4 D1 D2 D3 D4 E1 E2 E3 E4 F1 F2 F3 F4 G1 G2 G3 G4 H1 H2 H3 H4 I1 I2 I3 I4
      - 10�`20��ځA��ԁA�ȉ��֎~�ʒu
    - �����s�w���
  - MaxMoves�F�ۑ�ǖʂ���̎v�l�ΏۂƂȂ�ő�萔
  - BestPVFile�F�őP����Q���ꎞ�ۑ������t�@�C��
  - CommandFile�F��˂��牤�ւ̃R�}���h���ꎞ�ۑ������t�@�C��
  - YaneuraDBFile�F�ǖʂ��Ƃ̒T�����ʂ���쐬������Ճt�@�C��
  - TeraShockDBFile�FYaneuraDBFile��T�����čőP����̕]���l�ōX�V���ꂽ��Ճt�@�C��
  - MaxLoops�F��Չ����̉�
  - BlackResignValue�F��ՒT�����I��������̕]���l(���ڐ�)
  - WhiteResignValue�F��ՒT�����I��������̕]���l(���ڐ�)
  - CorrectionValue�F�T���[���ɔ�Ⴕ�ĕ]���l��␳����p�����[�^(-log2(depth+1)*)
    - ���l��傫������قǁA�]���l�������Ă��T���̐󂢎�𒲂ׂ�悤�ɂȂ�
    - 0���ƍőP�����ʂ̎菇�𒲂ׂ�
  - AutoMultiPV�F1�ǖʂɂ�����T���萔
  - MinMultiPV�F�ŏ����萔
    - AutoMultiPV��no�̏ꍇ�͏�ɂ��̒l�ƂȂ�
  - MaxMultiPV�F�ő���萔
    - AutoMultiPV��yes�̏ꍇ�̂ݗL��