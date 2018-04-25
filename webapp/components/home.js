import preact from 'preact';


export default () => (<div class="pure-g">
  <div class="pure-u">
    <h1>Strong passwords for humans</h1>
    <p class="faded">Making and remembering strong passwords is such a pain. And password managers will save your passwords in a way that they can read them. Ouch!</p>
    <h2>How does passfoo work?</h2>
    <p class="faded">We ask you some personal questions <u>everytime</u> (<span class="faded">unless you are logged in</span>) you need a new or existing password. The set of questions that you would like to answer is called a <b>Source</b> and is also selected by you.</p>
    <h2>Generated, but not stored</h2>
    <p class="faded">We do not store the sources (question banks), personal answers or passwords. We just store the mechanism to get a password from your own answers. Thus we never know your passowrd.</p>
    <h2>Complete security, little effort</h2>
    <p class="faded">Yes this is really as secure as password management can get, but you have to type in your answers the same way every time you need your password.</p>
  </div>
</div>);
