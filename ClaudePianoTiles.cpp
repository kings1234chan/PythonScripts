// Piano Tiles - a terminal game written in C++ with ncurses.
//
// Build:  g++ -std=c++17 -O2 piano_tiles.cpp -o piano_tiles -lncurses
// Run:    ./piano_tiles
//
// Rules: black tiles scroll down the four lanes. Tap the lowest tile
// (highlighted in blue) with the key for its lane: D F J K.
// Hit the wrong lane or let a tile reach the bottom and the game ends.
// The tiles speed up as your score grows.

#include <ncurses.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <deque>
#include <random>
#include <string>

constexpr int LANES   = 4;
constexpr int LANE_W  = 9;   // includes one separator column
constexpr int TILE_H  = 4;   // tile height in terminal rows
constexpr int FIELD_H = 20;  // playfield height in terminal rows
constexpr int ORIGIN_X = 2;
constexpr int ORIGIN_Y = 3;

enum Pair { P_FIELD = 1, P_TILE, P_NEXT, P_HIT, P_TEXT, P_BAD };

struct Tile {
    int   lane;
    float y;  // row of the tile's top edge (can be negative = above the screen)
};

class Game {
public:
    Game() : rng_(std::random_device{}()) { reset(); }

    void reset() {
        tiles_.clear();
        score_ = 0;
        over_ = false;
        reason_.clear();
        flashLane_ = -1;
        flashTime_ = 0.f;
        // The first tile starts a little above the bottom.
        tiles_.push_back({randomLane(), static_cast<float>(FIELD_H - 2 * TILE_H)});
        fillAbove();
    }

    // Rows per second; ramps up with score.
    float speed() const { return std::min(6.0f + score_ * 0.18f, 26.0f); }

    void update(float dt) {
        if (over_) return;
        for (auto& t : tiles_) t.y += speed() * dt;
        fillAbove();
        if (flashTime_ > 0.f) flashTime_ -= dt;

        if (tiles_.front().y >= FIELD_H) {
            over_ = true;
            reason_ = "You missed a tile!";
            if (score_ > best_) best_ = score_;
        }
    }

    void press(int lane) {
        if (over_) return;
        if (lane == tiles_.front().lane) {
            tiles_.pop_front();
            ++score_;
            flashLane_ = lane;
            flashTime_ = 0.08f;
        } else {
            over_ = true;
            reason_ = "Wrong lane!";
            if (score_ > best_) best_ = score_;
        }
    }

    bool over() const { return over_; }
    int  score() const { return score_; }
    int  best() const { return best_; }
    const std::string& reason() const { return reason_; }
    const std::deque<Tile>& tiles() const { return tiles_; }
    int  flashLane() const { return flashTime_ > 0.f ? flashLane_ : -1; }

private:
    int randomLane() {
        return std::uniform_int_distribution<int>(0, LANES - 1)(rng_);
    }
    // Keep a continuous stack of tiles extending above the screen.
    void fillAbove() {
        while (tiles_.back().y > -TILE_H) {
            tiles_.push_back({randomLane(), tiles_.back().y - TILE_H});
        }
    }

    std::deque<Tile> tiles_;  // front = lowest (next to tap)
    std::mt19937 rng_;
    int   score_ = 0;
    int   best_ = 0;
    bool  over_ = false;
    std::string reason_;
    int   flashLane_ = -1;
    float flashTime_ = 0.f;
};

static void fillCells(int row, int lane, int pair) {
    if (row < 0 || row >= FIELD_H) return;
    attron(COLOR_PAIR(pair));
    mvhline(ORIGIN_Y + row, ORIGIN_X + lane * LANE_W + 1, ' ', LANE_W - 1);
    attroff(COLOR_PAIR(pair));
}

static void draw(const Game& g) {
    erase();

    attron(COLOR_PAIR(P_TEXT) | A_BOLD);
    mvprintw(0, ORIGIN_X, "PIANO TILES");
    attroff(A_BOLD);
    mvprintw(1, ORIGIN_X, "Score: %-5d Best: %-5d Speed: %.1f", g.score(), g.best(), g.speed());
    attroff(COLOR_PAIR(P_TEXT));

    // Field background and lane separators.
    for (int r = 0; r < FIELD_H; ++r) {
        attron(COLOR_PAIR(P_FIELD));
        mvhline(ORIGIN_Y + r, ORIGIN_X, ' ', LANES * LANE_W + 1);
        for (int l = 0; l <= LANES; ++l) mvaddch(ORIGIN_Y + r, ORIGIN_X + l * LANE_W, '|');
        attroff(COLOR_PAIR(P_FIELD));
    }

    // Tiles (front tile is the one to tap next).
    bool first = true;
    for (const auto& t : g.tiles()) {
        int top = static_cast<int>(std::floor(t.y));
        int pair = first ? P_NEXT : P_TILE;
        for (int i = 0; i < TILE_H; ++i) fillCells(top + i, t.lane, pair);
        first = false;
    }

    // Brief flash on a successful hit.
    if (g.flashLane() >= 0) {
        attron(COLOR_PAIR(P_HIT));
        mvhline(ORIGIN_Y + FIELD_H, ORIGIN_X + g.flashLane() * LANE_W + 1, ' ', LANE_W - 1);
        attroff(COLOR_PAIR(P_HIT));
    }

    // Key labels.
    const char keys[LANES] = {'D', 'F', 'J', 'K'};
    attron(COLOR_PAIR(P_TEXT) | A_BOLD);
    for (int l = 0; l < LANES; ++l)
        mvprintw(ORIGIN_Y + FIELD_H + 1, ORIGIN_X + l * LANE_W + LANE_W / 2, "%c", keys[l]);
    attroff(A_BOLD);
    mvprintw(ORIGIN_Y + FIELD_H + 3, ORIGIN_X, "Q: quit");
    attroff(COLOR_PAIR(P_TEXT));

    if (g.over()) {
        const int w = 26, h = 7;
        int x = ORIGIN_X + (LANES * LANE_W + 1 - w) / 2;
        int y = ORIGIN_Y + (FIELD_H - h) / 2;
        attron(COLOR_PAIR(P_BAD) | A_BOLD);
        for (int r = 0; r < h; ++r) mvhline(y + r, x, ' ', w);
        mvprintw(y + 1, x + (w - 9) / 2, "GAME OVER");
        mvprintw(y + 3, x + (w - static_cast<int>(g.reason().size())) / 2, "%s", g.reason().c_str());
        std::string s = "Score: " + std::to_string(g.score());
        mvprintw(y + 4, x + (w - static_cast<int>(s.size())) / 2, "%s", s.c_str());
        mvprintw(y + 5, x + 2, "R: retry     Q: quit");
        attroff(COLOR_PAIR(P_BAD) | A_BOLD);
    }

    refresh();
}

int main() {
    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    nodelay(stdscr, TRUE);
    curs_set(0);

    if (LINES < ORIGIN_Y + FIELD_H + 4 || COLS < ORIGIN_X + LANES * LANE_W + 2) {
        endwin();
        std::fprintf(stderr, "Terminal too small: need at least %d x %d.\n",
                     ORIGIN_X + LANES * LANE_W + 2, ORIGIN_Y + FIELD_H + 4);
        return 1;
    }

    start_color();
    use_default_colors();
    init_pair(P_FIELD, COLOR_BLACK, COLOR_WHITE);
    init_pair(P_TILE, COLOR_WHITE, COLOR_BLACK);
    init_pair(P_NEXT, COLOR_WHITE, COLOR_BLUE);
    init_pair(P_HIT, COLOR_BLACK, COLOR_GREEN);
    init_pair(P_TEXT, COLOR_WHITE, -1);
    init_pair(P_BAD, COLOR_WHITE, COLOR_RED);

    Game game;
    auto last = std::chrono::steady_clock::now();
    bool running = true;

    while (running) {
        auto now = std::chrono::steady_clock::now();
        float dt = std::chrono::duration<float>(now - last).count();
        last = now;
        dt = std::min(dt, 0.05f);

        int ch;
        while ((ch = getch()) != ERR) {
            switch (ch) {
                case 'q': case 'Q': running = false; break;
                case 'r': case 'R': if (game.over()) game.reset(); break;
                case 'd': case 'D': game.press(0); break;
                case 'f': case 'F': game.press(1); break;
                case 'j': case 'J': game.press(2); break;
                case 'k': case 'K': game.press(3); break;
                default: break;
            }
        }

        game.update(dt);
        draw(game);
        napms(12);
    }

    endwin();
    return 0;
}
