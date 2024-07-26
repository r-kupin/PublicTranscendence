const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Score contract", function () {
    let Score;
    let score;
    let owner;
    let nonOwner;

    before(async function () {
        Score = await ethers.getContractFactory("Score");
        [owner, nonOwner] = await ethers.getSigners();
        score = await Score.deploy();
    });

    describe("Deployment", function () {
        it("Should set the right owner", async function () {
            expect(await score.owner()).to.equal(owner.address);
        });

        it("Initial counter should be 1", async function () {
            expect(await score.counter()).to.equal(1);
        });
    });

    describe("saveGameScore function", function () {
        it("Should save game score correctly when called by owner", async function () {
            const player1 = "Alice";
            const player2 = "Bob";
            const player1Score = 5;
            const player2Score = 3;

            await expect(score.saveGameScore(player1, player2, player1Score, player2Score))
                .to.emit(score, "GameSaved")
                .withArgs(player1, player2, player1Score, player2Score);

            const game = await score.games(1);
            expect(game.player1).to.equal(player1);
            expect(game.player2).to.equal(player2);
            expect(game.player1Score).to.equal(player1Score);
            expect(game.player2Score).to.equal(player2Score);
        });

        it("Should increment the counter after saving a game score", async function () {
            const player1 = "Charlie";
            const player2 = "Dana";
            const player1Score = 7;
            const player2Score = 2;

            await score.saveGameScore(player1, player2, player1Score, player2Score);
            expect(await score.counter()).to.equal(3);
        });

		it("Should revert when non-owner tries to save game score", async function () {
			const player1 = "Eve";
			const player2 = "Frank";
			const player1Score = 4;
			const player2Score = 1;
		
			// Expect generic revert instead of a specific message
			await expect(score.connect(nonOwner).saveGameScore(player1, player2, player1Score, player2Score))
				.to.be.reverted;
		});
    });
});
