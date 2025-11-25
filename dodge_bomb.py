import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内にあるかを判定し，真理値タプルを返す関数
    引数：こうかとんRect or 爆弾Rect
    戻り値：タプル（横方向判定結果，縦方向判定結果）
    画面内ならTrue，画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に画面を暗くし、メッセージと泣くこうかとんを表示する関数
    引数：screen Surface
    """
    # 画面を暗くする（半透明の黒いSurfaceを重ねる）
    gameover_bg = pg.Surface((WIDTH, HEIGHT))
    gameover_bg.set_alpha(200)
    gameover_bg.fill((0, 0, 0))
    screen.blit(gameover_bg, (0, 0))
    
    # Game Over 文字列
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH/2, HEIGHT/2))
    screen.blit(txt, txt_rct)
    
    # 泣いているこうかとん
    kk_cry = pg.image.load("fig/8.png") 
    kk_cry = pg.transform.rotozoom(kk_cry, 0, 0.9)
    # 左右に配置
    screen.blit(kk_cry, (WIDTH/2 - 200, HEIGHT/2 - 50))
    screen.blit(kk_cry, (WIDTH/2 + 150, HEIGHT/2 - 50))

    pg.display.update()
    time.sleep(5)


def init_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量に対応するこうかとん画像の辞書を生成する関数
    戻り値：移動量タプルをキー、画像Surfaceを値とする辞書
    """
    kk_img = pg.image.load("fig/3.png")
    kk_img = pg.transform.rotozoom(kk_img, 0, 0.9)
    
    return {
        (0, 0): kk_img,
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_img, -45, 1.0),
        (0, -5): pg.transform.rotozoom(kk_img, -90, 1.0),
        (+5, -5): pg.transform.flip(pg.transform.rotozoom(kk_img, -45, 1.0), True, False),
        (+5, 0): pg.transform.flip(kk_img, True, False),
        (+5, +5): pg.transform.flip(pg.transform.rotozoom(kk_img, 45, 1.0), True, False),
        (0, +5): pg.transform.rotozoom(kk_img, 90, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_img, 45, 1.0),
    }


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾画像のリストと加速度リストを生成する関数
    戻り値：(爆弾画像リスト, 加速度リスト)
    """
    bb_imgs = []
    accs = [a for a in range(1, 11)] # 加速度リスト（簡易化のため10段階に変更、必要なら戻してください）
    
    for r in range(1, 11): # 半径を段階的に変える
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
        
    return bb_imgs, accs


def get_kk_img(sum_mv: tuple[int, int], kk_imgs: dict) -> pg.Surface:
    """
    移動量の合計値から適切なこうかとん画像を取得する関数
    """
    return kk_imgs.get(sum_mv, kk_imgs[(0, 0)])


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    
    # こうかとん画像の初期化
    kk_imgs = init_kk_imgs()
    kk_rct = kk_imgs[(0, 0)].get_rect()
    kk_rct.center = 300, 200

    # 爆弾画像の初期化
    bb_imgs, accs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        # 背景描画
        screen.blit(bg_img, [0, 0]) 

        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        
        # こうかとん描画（関数利用）
        kk_img_curr = get_kk_img(tuple(sum_mv), kk_imgs)
        screen.blit(kk_img_curr, kk_rct)

        # 爆弾の加速と拡大処理
        idx = min(tmr // 500, 9) 
        bb_img_curr = bb_imgs[idx]
        bb_rct = bb_img_curr.get_rect(center=bb_rct.center)
        
        # 簡易化のため accs[idx] を使って計算
        avx = vx * accs[idx] 
        avy = vy * accs[idx]
        
        bb_rct.move_ip(avx, avy)
        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
            
        screen.blit(bb_img_curr, bb_rct)

        # ゲームオーバー判定
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()