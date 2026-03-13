export default class AIEngine {

constructor(){

this.correctStreak = 0
this.wrongStreak = 0

this.level = "easy"

}

recordResult(correct){

if(correct){

this.correctStreak++
this.wrongStreak = 0

}else{

this.wrongStreak++
this.correctStreak = 0

}

this.updateDifficulty()

}

updateDifficulty(){

if(this.correctStreak >= 3){

if(this.level === "easy")
this.level = "medium"

else if(this.level === "medium")
this.level = "hard"

this.correctStreak = 0

}

if(this.wrongStreak >= 2){

if(this.level === "hard")
this.level = "medium"

else if(this.level === "medium")
this.level = "easy"

this.wrongStreak = 0

}

}

getDifficulty(){

return this.level

}

}