// Piano Tiles - a small graphical game written in C++ using SFML 2.5/2.6
// Controls: A / S / K / L (or click tiles). Press SPACE to start/restart, ESC to quit.

#include <SFML/Graphics.hpp>
#include <algorithm>
#include <array>
#include <random>
#include <string>
#include <vector>

namespace {
constexpr unsigned WINDOW_W = 900;
constexpr unsigned WINDOW_H = 720;
constexpr float BOARD_X = 210.f;
constexpr float BOARD_Y = 100.f;
constexpr float BOARD_W = 480.f;
constexpr float BOARD_H = 600.f;
constexpr float LANE_W = BOARD_W / 4.f;
constexpr float TILE_H = 115.f;
constexpr float ROW_STEP = 125.f;

struct TileRow {
    float y{};       // Relative to the top of the play board
    int lane{};      // Which lane contains the black tile (0..3)
    bool hit{};
};

enum class GameState { Ready, Playing, GameOver };

std::mt19937 rng{std::random_device{}()};
std::vector<TileRow> rows;
GameState state = GameState::Ready;
int score = 0;
float speed = 190.f;
float spawnTimer = 0.f;
sf::Font font;
bool fontLoaded = false;

int randomLane(int previousLane = -1) {
    std::uniform_int_distribution<int> dist(0, 3);
    int lane = dist(rng);
    // Avoid too many identical lanes in a row without making the pattern predictable.
    if (previousLane >= 0 && lane == previousLane) {
        lane = (lane + 1 + (dist(rng) % 3)) % 4;
    }
    return lane;
}

void loadFont() {
    const std::array<std::string, 5> paths = {
        "arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf"
    };
    for (const auto& path : paths) {
        if (font.loadFromFile(path)) {
            fontLoaded = true;
            return;
        }
    }
}

void resetGame() {
    rows.clear();
    score = 0;
    speed = 190.f;
    spawnTimer = 0.f;
    int previousLane = -1;
    // Fill the upper part of the board with rows that scroll down.
    for (int i = 5; i >= 1; --i) {
        int lane = randomLane(previousLane);
        rows.push_back(TileRow{-static_cast<float>(i) * ROW_STEP, lane, false});
        previousLane = lane;
    }
    state = GameState::Playing;
}

void endGame() {
    state = GameState::GameOver;
}

void hitLane(int lane) {
    if (state != GameState::Playing) return;

    // Pick the lowest visible, unhit black tile in this lane.
    TileRow* candidate = nullptr;
    for (auto& row : rows) {
        const bool visible = row.y + TILE_H > 0.f && row.y < BOARD_H;
        if (visible && row.lane == lane && !row.hit) {
            if (!candidate || row.y > candidate->y) candidate = &row;
        }
    }

    if (candidate) {
        candidate->hit = true;
        ++score;
        speed = std::min(500.f, 190.f + static_cast<float>(score) * 5.f);
    } else {
        // Pressing a lane with no available black tile is a miss.
        endGame();
    }
}

void handleMouseClick(sf::Vector2i mouse) {
    if (state != GameState::Playing) return;
    const float mx = static_cast<float>(mouse.x);
    const float my = static_cast<float>(mouse.y);
    if (mx < BOARD_X || mx >= BOARD_X + BOARD_W ||
        my < BOARD_Y || my >= BOARD_Y + BOARD_H) return;

    const int lane = std::clamp(static_cast<int>((mx - BOARD_X) / LANE_W), 0, 3);
    const float localY = my - BOARD_Y;
    TileRow* clickedRow = nullptr;
    for (auto& row : rows) {
        if (localY >= row.y && localY < row.y + TILE_H) {
            clickedRow = &row;
            break;
        }
    }

    if (!clickedRow) return; // Ignore clicks in the small gaps between rows.
    if (clickedRow->lane == lane && !clickedRow->hit) {
        clickedRow->hit = true;
        ++score;
        speed = std::min(500.f, 190.f + static_cast<float>(score) * 5.f);
    } else if (clickedRow->lane != lane) {
        endGame(); // White tile clicked.
    }
}

void update(float dt) {
    if (state != GameState::Playing) return;

    for (auto& row : rows) {
        row.y += speed * dt;
        // The bottom edge of an unhit black tile reaching the board's bottom is a miss.
        if (row.y + TILE_H >= BOARD_H && !row.hit) {
            endGame();
            return;
        }
    }

    // The rows are ordered from top to bottom. Recycle the bottom row once it leaves.
    while (!rows.empty() && rows.back().y >= BOARD_H) {
        const int previousLane = rows.front().lane;
        rows.pop_back();
        const int lane = randomLane(previousLane);
        const float newY = rows.front().y - ROW_STEP;
        rows.insert(rows.begin(), TileRow{newY, lane, false});
    }
}

void drawText(sf::RenderWindow& window, const std::string& value,
              unsigned size, float x, float y, sf::Color color,
              bool centered = false) {
    if (!fontLoaded) return;
    sf::Text text(value, font, size);
    text.setFillColor(color);
    if (centered) {
        const sf::FloatRect bounds = text.getLocalBounds();
        text.setOrigin(bounds.left + bounds.width / 2.f,
                       bounds.top + bounds.height / 2.f);
    }
    text.setPosition(x, y);
    window.draw(text);
}

void drawGame(sf::RenderWindow& window) {
    window.clear(sf::Color(21, 25, 35));

    // Header
    drawText(window, "PIANO TILES", 34, WINDOW_W / 2.f, 28.f,
             sf::Color(245, 247, 255), true);
    drawText(window, "SCORE  " + std::to_string(score), 22, BOARD_X, 74.f,
             sf::Color(93, 230, 200));
    drawText(window, "SPEED  " + std::to_string(static_cast<int>(speed)), 16,
             BOARD_X + BOARD_W - 120.f, 78.f, sf::Color(190, 198, 215));

    // Board background
    sf::RectangleShape board({BOARD_W, BOARD_H});
    board.setPosition(BOARD_X, BOARD_Y);
    board.setFillColor(sf::Color(45, 51, 66));
    window.draw(board);

    // Draw the four tile lanes for each visible row.
    for (const auto& row : rows) {
        if (row.y + TILE_H <= 0.f || row.y >= BOARD_H) continue;
        for (int lane = 0; lane < 4; ++lane) {
            sf::RectangleShape tile({LANE_W - 3.f, TILE_H - 2.f});
            tile.setPosition(BOARD_X + lane * LANE_W + 1.5f,
                             BOARD_Y + row.y + 1.f);
            tile.setOutlineThickness(1.f);
            tile.setOutlineColor(sf::Color(190, 198, 210));
            if (lane == row.lane) {
                tile.setFillColor(row.hit ? sf::Color(41, 190, 153)
                                          : sf::Color(13, 16, 23));
            } else {
                tile.setFillColor(sf::Color(244, 246, 250));
            }
            window.draw(tile);
        }
    }

    // Subtle board border
    sf::RectangleShape border({BOARD_W, BOARD_H});
    border.setPosition(BOARD_X, BOARD_Y);
    border.setFillColor(sf::Color::Transparent);
    border.setOutlineThickness(3.f);
    border.setOutlineColor(sf::Color(91, 105, 128));
    window.draw(border);

    drawText(window, "A", 18, BOARD_X + LANE_W * 0.5f, 708.f,
             sf::Color(205, 213, 226), true);
    drawText(window, "S", 18, BOARD_X + LANE_W * 1.5f, 708.f,
             sf::Color(205, 213, 226), true);
    drawText(window, "K", 18, BOARD_X + LANE_W * 2.5f, 708.f,
             sf::Color(205, 213, 226), true);
    drawText(window, "L", 18, BOARD_X + LANE_W * 3.5f, 708.f,
             sf::Color(205, 213, 226), true);

    if (state == GameState::Ready || state == GameState::GameOver) {
        sf::RectangleShape shade({BOARD_W, BOARD_H});
        shade.setPosition(BOARD_X, BOARD_Y);
        shade.setFillColor(sf::Color(9, 12, 19, 205));
        window.draw(shade);

        if (state == GameState::Ready) {
            drawText(window, "READY?", 42, WINDOW_W / 2.f, 270.f,
                     sf::Color(255, 255, 255), true);
            drawText(window, "Hit the black tiles", 22, WINDOW_W / 2.f, 325.f,
                     sf::Color(93, 230, 200), true);
            drawText(window, "A / S / K / L  or click", 18,
                     WINDOW_W / 2.f, 365.f, sf::Color(220, 225, 236), true);
            drawText(window, "Press SPACE to start", 18,
                     WINDOW_W / 2.f, 415.f, sf::Color(220, 225, 236), true);
        } else {
            drawText(window, "GAME OVER", 42, WINDOW_W / 2.f, 270.f,
                     sf::Color(255, 116, 129), true);
            drawText(window, "Score: " + std::to_string(score), 26,
                     WINDOW_W / 2.f, 330.f, sf::Color(255, 255, 255), true);
            drawText(window, "Press SPACE to try again", 18,
                     WINDOW_W / 2.f, 390.f, sf::Color(220, 225, 236), true);
        }
    }

    window.display();
}
} // namespace

int main() {
    loadFont();
    sf::RenderWindow window(sf::VideoMode(WINDOW_W, WINDOW_H),
                            "Piano Tiles - C++", sf::Style::Titlebar | sf::Style::Close);
    window.setFramerateLimit(60);
    sf::Clock clock;

    while (window.isOpen()) {
        const float dt = std::min(clock.restart().asSeconds(), 0.05f);
        sf::Event event{};
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            } else if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Escape) {
                    window.close();
                } else if (event.key.code == sf::Keyboard::Space && state != GameState::Playing) {
                    resetGame();
                } else if (state == GameState::Playing) {
                    switch (event.key.code) {
                        case sf::Keyboard::A: hitLane(0); break;
                        case sf::Keyboard::S: hitLane(1); break;
                        case sf::Keyboard::K: hitLane(2); break;
                        case sf::Keyboard::L: hitLane(3); break;
                        default: break;
                    }
                }
            } else if (event.type == sf::Event::MouseButtonPressed &&
                       event.mouseButton.button == sf::Mouse::Left) {
                if (state == GameState::Ready || state == GameState::GameOver) {
                    // Clicking the board's overlay starts or restarts the game.
                    resetGame();
                } else {
                    handleMouseClick(sf::Mouse::getPosition(window));
                }
            }
        }

        update(dt);
        drawGame(window);
    }
    return 0;
}
