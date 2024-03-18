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

async function logVote(voteJSON) {
    const response = await fetch("/vote", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(voteJSON),
    });
    const data = await response.json();
    alert(data.message);
    return await data;
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
    if (allRanksAboveZero(candidates) && voterName !== "" && voterName !== " " && voterName !== null) {
        alert("Vote Submitted!");
        logVote(voteResult);
    } else {
        alert("You must rank all candidates! And you must enter your name!");
    }
}

function getResults() {
    
}