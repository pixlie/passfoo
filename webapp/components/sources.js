import { Component } from 'preact';

import { fetchQuestionList } from '../actions/password';


export default class Sources extends Component {
  constructor() {
    super();
    this.state = {
      questions: []
    };
    this.setQuestions = this.setQuestions.bind(this);
  }

  setQuestions(questions) {
    this.setState({
      questions: questions
    });
  }

  componentDidMount() {
    fetchQuestionList(this.setQuestions);
  }

  render(props, {questions}) {
    return (<div class="pure-g list">
      <div class="pure-u-1">
        <div class="question-item">
          <h1>Questions</h1>
          <p class="faded">In order for passfoo to generate passwords for you, we need you to select a set of information that you will provide every time you need the password.</p>
          <h2 class="email-name">Names/dates that you want to use</h2>
          <p class="faded">passfoo will never store this information or the passwords, thus you will have to enter the same information every time you need your password.</p>
          <p class="faded">That might seem like a lot of work, but this is what makes passfoo really secure.</p>
        </div>
      </div>

      <div class="pure-u-1">
        <form class="pure-form pure-form-stacked">
          {questions.map((q, i) => {
            if (q.related_id === null) {
              return <label for={`id-${q.id}`}>
                <input type="checkbox" id={`id-${q.id}`} name={`"q-${q.id}`} /> {q.text}
              </label>;
            }
          })}

          <input type="submit" value="New password" class="pure-button pure-button-primary" disabled />
        </form>
      </div>
    </div>);
  }
}
