document.addEventListener('DOMContentLoaded', function() {

  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email)

  load_mailbox('inbox');
});

function compose_email() {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#mail-view').style.display = 'none';

  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'none';


  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Print emails
    console.log(emails);

    emails.forEach( email => {
      const newEmail = document.createElement('div');
      newEmail.className = email.read ? 'list-group-item read': 'list-group-item noread';
      newEmail.innerHTML = `
      <h5>Sender: ${email.sender}</h5>
      <h4>Subject: ${email.subject}</h4>
      <p>${email.timestamp}</p>
      `;

      newEmail.addEventListener('click', () => email_view(email.id));
      document.querySelector('#emails-view').append(newEmail);
    })
  });
}

function send_email() {
  event.preventDefault();
  const recipients = document.querySelector('#compose-recipients').value
  const subject = document.querySelector('#compose-subject').value
  const body = document.querySelector('#compose-body').value
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent')
  });
}

function email_view(id) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#mail-view').style.display = 'block';


  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    console.log(email);

    document.querySelector('#mail-view').innerHTML = `
    <ul class='list-group'>
      <li class='list-group-item'><strong>From: </strong>${email.sender}</li>
      <li class='list-group-item'><strong>To: </strong>${email.recipients}</li>
      <li class='list-group-item'><strong>Subject: </strong>${email.subject}</li>
      <li class='list-group-item'><strong>Timestamp: </strong>${email.timestamp}</li>
      <li class='list-group-item'>${email.body}</li>
    </ul>
    <button id='archive' class='btn-info'></button>
    <button id='reply' class='btn-info'>Reply</button>
    `
    if (!email.read) {
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      });
    }

    const archive = document.getElementById('archive');
    archive.innerHTML = email.archived ? 'Unarchive': 'Archive';
    archive.className = email.archived ? 'btn-danger': 'btn-success';
    archive.addEventListener('click', ()=>{
      fetch(`/emails/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: !email.archived
        })
      });
      if (archive.innerHTML === 'Unarchive') {
        archive.innerHTML = 'Archive';
        archive.className = 'btn-success';
      }
      else {
        archive.innerHTML = 'Unarchive';
        archive.className = 'btn-danger';
      }
    })
    document.querySelector('#reply').addEventListener('click', () => {
      document.querySelector('#emails-view').style.display = 'none';
      document.querySelector('#compose-view').style.display = 'block';
      document.querySelector('#mail-view').style.display = 'none';

      let subject = email.subject;
      if (subject.split(' ',1)[0] !== 'Re:') {
        subject = 'Re: ' + subject;
      }
      document.querySelector('#compose-recipients').value = `${email.sender}`;
      document.querySelector('#compose-subject').value = `${subject}`;
      document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:${email.body}`;
    });
  });
}
