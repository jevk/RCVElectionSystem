class Candidate {
    constructor(name) {
        this.name = name;
        this.rank = 0;
    }

    getRank() {
        return this.rank;
    }

    getName() {
        return this.name;
    }

    setRank(rank) {
        this.rank = rank;
    }

    setName(name) {
        this.name = name;
    }
}

class VoteResult {
    constructor(candidates, voterName) {
        this.candidates = candidates;
        this.voterName = voterName;
    }
}

function allRanksAboveZero(objects) {
    for (let i = 0; i < objects.length; i++) {
        if (objects[i].getRank() === 0) {
            return false;
        }
    }
    return true;
}

function sendResults() {
    const candidates = [];
    const entries = document.getElementsByName("candidate-name");
    const voterName = document.getElementById("voter-name").value;
    entries.forEach((c) => {
        const name = c.textContent;
        const candidate = new Candidate(name);

        for (let i = 1; i <= entries.length; i++) {
            const voteNumber = name + i;
            const vote = document.getElementById(voteNumber);

            if (vote.checked) {
                candidate.setRank(i);
                break;
            } else {
                candidate.setRank(0);
            }
        }
        candidates.push(candidate);
    });
    const voteResult = new VoteResult(candidates, voterName);
    fetch("https://api.earthmc.net/v1/aurora/nations/Finland", { mode: "no-cors"}).then((response) => {
        console.log(response);
    });
    if (allRanksAboveZero(candidates)) {
        fetch("/vote", {
            method: "POST",
            body: JSON.stringify(voteResult),
            headers: {
                "Content-Type": "application/json; charset=utf-8",
            }
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Request failed!");
        });
        alert("Vote Submitted!");
    } else {
        alert("You must rank all candidates!");
    }
}