import pyxel

TILE_NULL = (0,0)
TILE_MISSILE = (1,0)
TILE_FUEL = (2,0)
TILE_BASE = (3,0)
TILE_ALT_MISSILE = (11,0)
TILE_ALT_FUEL = (12,0)
TILE_ALT_BASE = (13,0)
D = [[0,1],[0,-1],[1,0],[-1,0]]  ## 下、上、右、左
KEY = [pyxel.KEY_DOWN,pyxel.KEY_UP,pyxel.KEY_RIGHT,pyxel.KEY_LEFT]
LAXIS = [pyxel.GAMEPAD1_AXIS_LEFTY,pyxel.GAMEPAD1_AXIS_LEFTY,
         pyxel.GAMEPAD1_AXIS_LEFTX,pyxel.GAMEPAD1_AXIS_LEFTX]
LAXIS_RANGE = [[20000,36000],[-36000,-20000],[20000,36000],[-36000,-20000]]
GPAD = [pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
        pyxel.GAMEPAD1_BUTTON_DPAD_UP,
        pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
        pyxel.GAMEPAD1_BUTTON_DPAD_LEFT]

frame_x = 0
missiles = []
fuels = []
bases = []
beams = []
bombs = []
explos = []

class MyShip():
    def __init__(self) -> None:
        self.x = frame_x+10
        self.y = 30
        self.is_alive = True
        #self.is_controllable = True
        self.cpoints = [[4,1], [2,8],[4,8],[6,8],[8,8],[10,8], [14,1], [14,8] ]
    def update(self):
        self.x += 1
    def draw(self):
        pyxel.blt(self.x-frame_x,self.y,0,pyxel.frame_count%3*16,72,16,8,0)
    def is_cd(self):
        rc = False
        for x,y in self.cpoints:
            if pyxel.pget(self.x-frame_x+x,self.y+y) != 0:
                rc = True
                self.is_alive = False
                break
        return rc
myship = MyShip()

class Missile():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.dy = pyxel.rndf(-1.4,-1)
        self.cnt = pyxel.rndi(0,80)
        self.is_fly = False
        self.is_alive = True
    def update(self):
        if self.is_fly:
            self.y += self.dy
            if self.y < -10:
                    self.is_alive = False
            elif pyxel.pget(self.x-frame_x+8,self.y//1-1)!=0:
                self.is_alive = False
        else:
            self.cnt -= 1
            if self.cnt < 0:
                self.is_fly = True

    def draw(self):
        if self.is_fly:
            pyxel.blt(self.x-frame_x,self.y, 0, 8+self.y//1%3*8,64, 8,8, 0)
        else:
            pyxel.blt(self.x-frame_x,self.y, 0, 0,64, 8,8, 0)

class Fuel():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.is_alive = True
    def update(self):
        if frame_x > self.x+10:
            self.is_alive = False
    def draw(self):
        pyxel.blt(self.x-frame_x,self.y, 0, pyxel.frame_count//11%3*8,80, 8,8, 0)
class Base():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.is_alive = True
    def update(self):
        if frame_x > self.x+10:
            self.is_alive = False
    def draw(self):
        pyxel.blt(self.x-frame_x,self.y, 0, pyxel.frame_count//3%3*8,88, 8,8, 0)

class Beam():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.W = 3
        self.is_alive = True
    def update(self):
        self.x += 3
        if self.x-frame_x > 120:
            self.is_alive = False
    def draw(self):
        pyxel.rect(self.x-frame_x,self.y,self.W,1,7)

class Bomb():
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.cnt = 0
        self.state = 0
        self.d = [ [2,0], [2,1], [2,4] ]
        self.is_alive = True
    def update(self):
        self.cnt += 1
        if self.cnt < 3:
            self.state = 0
        elif self.cnt < 9:
            self.state = 1
        else:
            self.state = 2
        self.x += self.d[self.state][0]
        self.y += self.d[self.state][1]
        if self.y > 120:
            self.is_alive = False
    def draw(self):
        pyxel.blt(self.x-frame_x,self.y,0,32+8*self.state,64,8,8,0)

class Explo():
    def __init__(self,x,y,cnt) -> None:
        self.x = x
        self.y = y
        self.cnt = cnt
        self.is_alive = True
    def update(self):
        self.cnt -= 1
        self.x += 1
        if self.cnt < 0:
            self.is_alive = False
    def draw(self):
        pyxel.blt(self.x-frame_x,self.y, 0, self.cnt%3*8,104, 8,8, 0)



class App():
    def __init__(self):
        pyxel.init(120,120,title="Emergency Attacker",fps=24)
        pyxel.load("scramble.pyxres")
        self.stage_num = 0
        self.tilemode_cnt = 80
        self.gameover_cnt = 0
        pyxel.run(self.update,self.draw)

    def init_game(self):
        global frame_x,missiles,fuels,bases,beams,bombs,explos,myship
        self.score = 0
        self.fuelvalue = 2500
        #self.stage_num = 0
        frame_x = -220
        missiles = []
        fuels = []
        bases = []
        beams = []
        bombs = []
        explos = []
        myship = MyShip()

    def update(self):
        global frame_x,missiles,fuels,bases
        ### タイトル表示モードのカウントダウン
        if self.tilemode_cnt > 0:
            self.tilemode_cnt -= 1
            if self.tilemode_cnt == 0:
                self.init_game()
            return
        ### ゲームオーバー時のカウントダウン
        if self.gameover_cnt > 0:
            self.gameover_cnt -= 1
            if self.gameover_cnt == 0:
                self.tilemode_cnt = 80
                return
        ### 背景のスクロール
        frame_x += 1
        ### 燃料減
        if self.fuelvalue > 0 and frame_x > 0 and self.gameover_cnt==0:
            self.fuelvalue -= 2
        ### 背景が右端まで来ちゃったのでステージ更新
        if frame_x > 2048:
            frame_x = -220
            myship.x = myship.x - 2049 - 220
            self.stage_num += 1
        ### 背景が表示しきれる（frame_xが0以上）になるまでは移動できないよ
        #if frame_x >= 0:
        #    myship.is_alive = True
        #else:
        #    myship.is_alive = False
        ### タイルマップの情報からオブジェクトを生成
        if frame_x%8==0:
            x = frame_x//8+15
            for y in range(16):
                tiley = self.stage_num*16+y
                tile = pyxel.tilemaps[0].pget(x,tiley)
                if tile==TILE_MISSILE or tile==TILE_ALT_MISSILE:
                    pyxel.tilemaps[0].pset(x,tiley,TILE_ALT_MISSILE)
                    missiles.append(Missile(x*8,(y-1)*8))
                elif tile==TILE_FUEL or tile==TILE_ALT_FUEL:
                    pyxel.tilemaps[0].pset(x,tiley,TILE_ALT_FUEL)
                    fuels.append(Fuel(x*8,(y-1)*8))
                elif tile==TILE_BASE or tile==TILE_ALT_BASE:
                    pyxel.tilemaps[0].pset(x,tiley,TILE_ALT_BASE)
                    bases.append(Base(x*8,(y-1)*8))
        ### マイシップがalive中の処理（ゲームオーバー判定、移動、ビーム発射、爆弾投下）
        if myship.is_alive:
            ### ゲームオーバーの判定
            if myship.is_cd():
                self.gameover_cnt = 100
                for i in range(12):
                    explos.append(Explo(myship.x+pyxel.rndi(-4,15),myship.y+pyxel.rndi(-4,8),pyxel.rndi(3,50)))
                myship.y = -100
                myship.is_alive = False
            else:
                ### 自キャラ移動の判定　：自キャラを移動
                if self.fuelvalue > 0: ## 燃料があれば移動できますが、
                    for i in range(4):
                        if pyxel.btn(KEY[i]) or (pyxel.btnv(LAXIS[i]) > LAXIS_RANGE[i][0] and pyxel.btnv(LAXIS[i]) < LAXIS_RANGE[i][1]) or pyxel.btn(GPAD[i]):
                            myship.x += D[i][0]
                            myship.y += D[i][1]
                    myship.x = max(myship.x,frame_x)
                    myship.x = min(frame_x+70,myship.x)
                    myship.y = max(myship.y,0)
                    myship.y = min(112,myship.y)
                else: ## 燃料が無いと落下するのみ
                    myship.y = min(112,myship.y+1)
                ### ビーム発射ボタンの判定
                if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                    if len(beams) < 4:
                        beams.append(Beam(myship.x+17,myship.y+4))
                        pyxel.play(1,1)
                ### 爆弾投下ボタンの判定
                if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
                    if len(bombs) < self.stage_num//2+1:
                        bombs.append(Bomb(myship.x+17,myship.y+8))
                        pyxel.play(0,0)

        ### マイシップの更新
        myship.update()
        ### ミサイルの更新
        for missile in reversed(missiles):
            missile.update()
            if not missile.is_alive:
                explos.append(Explo(missile.x,missile.y,3))
                missiles.remove(missile)
        ### 燃料タンクの更新
        for fuel in reversed(fuels):
            fuel.update()
            if not fuel.is_alive:
                explos.append(Explo(fuel.x,fuel.y,3))
                fuels.remove(fuel)
        ### 基地の更新
        for base in reversed(bases):
            base.update()
            if not base.is_alive:
                explos.append(Explo(base.x,base.y,3))
                bases.remove(base)
        ### 発射したビームの更新
        for beam in reversed(beams):
            beam.update()
            ### 敵物体との当たり判定
            if beam.is_alive:
                for missile in missiles:
                    if missile.x-beam.x < 5 and abs(missile.y+4-beam.y) < 4:
                        missile.is_alive = False
                        beam.is_alive = False
                        pyxel.play(2,2)
                        break
            if beam.is_alive:
                for fuel in fuels:
                    if fuel.x-beam.x < 5 and abs(fuel.y+4-beam.y) < 5:
                        self.fuelvalue = min(self.fuelvalue+400,2500)
                        fuel.is_alive = False
                        beam.is_alive = False
                        pyxel.play(2,2)
                        break
            if beam.is_alive:
                for base in bases:
                    if base.x-beam.x < 5 and abs(base.y+4-beam.y) < 5:
                        base.is_alive = False
                        beam.is_alive = False
                        pyxel.play(2,2)
                        break
            ### 壁などにぶつかって消滅
            if beam.is_alive:
                if pyxel.pget(beam.x-frame_x+beam.W,beam.y)!=0 and pyxel.pget(beam.x-frame_x+beam.W,beam.y)!=7:
                    explos.append(Explo(beam.x-4,beam.y-3,3))
                    beam.is_alive = False
                ### is_aliveを確認してremoveの処理
            if not beam.is_alive:
                beams.remove(beam)
        ### 投下した爆弾の更新
        for bomb in reversed(bombs):
            bomb.update()
            ### 敵物体との当たり判定
            if bomb.is_alive:
                for missile in missiles:
                    if abs(missile.x-bomb.x+2) < 7 and abs(missile.y-bomb.y+1) < 7:
                        missile.is_alive = False
                        bomb.is_alive = False
                        pyxel.play(2,2)
                        break
            if bomb.is_alive:
                for fuel in fuels:
                    if abs(fuel.x-bomb.x+2) < 7 and fuel.y-bomb.y < 8:
                        self.fuelvalue = min(self.fuelvalue+400,2500)
                        fuel.is_alive = False
                        bomb.is_alive = False
                        pyxel.play(2,2)
                        break
            if bomb.is_alive:
                for base in bases:
                    if abs(base.x-bomb.x+2) < 7 and base.y-bomb.y < 8:
                        base.is_alive = False
                        bomb.is_alive = False
                        pyxel.play(2,2)
                        break
            ### 地面などにぶつかって消滅
            if bomb.is_alive:
                if pyxel.pget(bomb.x+2-frame_x,bomb.y+6)!=0 and pyxel.pget(bomb.x+2-frame_x,bomb.y+6)!=10:
                    #print("{}  {},{}".format(frame_x,bomb.x+2,bomb.y+6))
                    explos.append(Explo(bomb.x+2,bomb.y-2,3))
                    bomb.is_alive = False
                ### is_aliveを確認してremoveの処理
            if not bomb.is_alive:
                bombs.remove(bomb)
        ### 爆破エフェクトの更新
        for explo in reversed(explos):
            explo.update()
            if not explo.is_alive:
                explos.remove(explo)

    def draw(self):
        ### タイトルモード時の描画
        if self.tilemode_cnt > 0:
            pyxel.cls(0)
            pyxel.blt(5,20, 1, 0,0, 110,34, 0)
            pyxel.blt(90-self.tilemode_cnt,70, 0, pyxel.frame_count%3*16,72, 16,8, 0)
            return

        ### ゲーム中の描画
        pyxel.cls(0)
        pyxel.bltm(0,0,  0,  frame_x,self.stage_num*128+8, 120,120, 0)

        ### マイシップの描画
        myship.draw()
        ### ミサイルの描画
        for missile in missiles:
            missile.draw()
        ### 燃料タンクの描画
        for fuel in reversed(fuels):
            fuel.draw()
        ### 基地の描画
        for base in reversed(bases):
            base.draw()
        ### ビームの描画
        for beam in reversed(beams):
            beam.draw()
        ### 爆弾の描画
        for bomb in reversed(bombs):
            bomb.draw()
        ### 爆破エフェクトの描画
        for explo in reversed(explos):
            explo.draw()

        ### 情報表示
        # 燃料ゲージ
        pyxel.rectb(90,1,27,3,12)
        pyxel.rect(91,2,25,1,13)
        if self.fuelvalue > 1400:
            pyxel.rect(91,2,self.fuelvalue//100,1,5)
        elif self.fuelvalue > 600:
            pyxel.rect(91,2,self.fuelvalue//100,1,9)
        else:
            pyxel.rect(91,2,self.fuelvalue//100,1,8)

        ### ステージ開始時だけのメッセージ表示
        if frame_x < 0:
            pyxel.text(90,7,"STAGE {}".format(self.stage_num+1),7)

        ### デバッグ用
        #pyxel.text(10,10,"len(missiles):{}".format(len(missiles)),7)
        #pyxel.text(10,20,"len(bombs):{}".format(len(bombs)),7)
        #pyxel.text(10,20,"len(fuels):{}".format(len(fuels)),7)
        #pyxel.text(10,30,"len(bases):{}".format(len(bases)),7)
        #pyxel.text(10,10,"frame_x:{}".format(frame_x),7)
        #pyxel.text(10,20,"myship.x:{}".format(myship.x),7)

App()

