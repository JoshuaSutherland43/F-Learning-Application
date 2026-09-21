var Views = window.Views = window.Views || {};

Views.dashboard = function (container) {
  return Api.getProgress().then(function (p) {
    const html = [];
    html.push('<h1 class="page-title">Dashboard</h1>');
    html.push('<p class="page-subtitle">If your exam were tomorrow, here is exactly what to study right now.</p>');

    if (p.study_now_recommendation) {
      html.push('<div class="card" style="border-color:var(--accent);">');
      html.push('<div class="card-title">Study this right now</div>');
      html.push('<div style="font-size:15px;font-weight:700;margin-bottom:6px;">' + escapeHtml((p.study_now_recommendation.topic_id || "").replace(/-/g, " ")) + '</div>');
      html.push(renderMarkdown(p.study_now_recommendation.reason || ""));
      html.push('<div class="btn-row"><a class="btn primary" href="#/learn/' + encodeURIComponent(p.study_now_recommendation.topic_id) + '">Go learn it</a>' +
        '<a class="btn" href="#/practice">Practice now</a></div>');
      html.push('</div>');
    }

    html.push('<div class="grid-3">');
    html.push(statTile(p.overall_coverage_percent + "%", "Curriculum coverage"));
    html.push(statTile(p.questions_attempted, "Questions attempted"));
    html.push(statTile(p.questions_correct + " / " + (p.questions_correct + p.questions_incorrect || 0), "Correct / total"));
    html.push('</div>');

    html.push('<div class="grid-2">');

    // Topic mastery
    html.push('<div class="card"><div class="card-title">Topic Mastery</div>');
    if (!p.topics || !p.topics.length) {
      html.push('<div class="empty-state" style="padding:20px;">No topics tracked yet.</div>');
    } else {
      p.topics.forEach(function (t) {
        html.push(masteryRow(t));
      });
    }
    html.push('</div>');

    // Weak / strong
    html.push('<div class="card">');
    html.push('<div class="card-title">Weak Topics</div>');
    if (p.weak_topics && p.weak_topics.length) {
      html.push('<div class="chip-row">' + p.weak_topics.map(function (t) {
        return '<a class="chip" href="#/learn/' + encodeURIComponent(t) + '">' + escapeHtml(t.replace(/-/g, " ")) + '</a>';
      }).join("") + '</div>');
    } else {
      html.push('<p style="color:var(--text-faint);font-size:13px;">None identified yet — keep practicing.</p>');
    }
    html.push('<div class="card-title" style="margin-top:16px;">Strong Topics</div>');
    if (p.strong_topics && p.strong_topics.length) {
      html.push('<div class="chip-row">' + p.strong_topics.map(function (t) {
        return '<span class="chip">' + escapeHtml(t.replace(/-/g, " ")) + '</span>';
      }).join("") + '</div>');
    } else {
      html.push('<p style="color:var(--text-faint);font-size:13px;">None identified yet.</p>');
    }
    html.push('</div>');

    html.push('</div>'); // grid-2

    html.push('<div class="grid-2">');

    // Recent activity
    html.push('<div class="card"><div class="card-title">Recent Activity</div>');
    if (p.recent_activity && p.recent_activity.length) {
      p.recent_activity.slice(0, 12).forEach(function (a) {
        const outcome = a.correct === true ? '<span class="status-strong">correct</span>' :
          a.correct === false ? '<span class="status-weak">incorrect</span>' :
          (typeof a.score_percent === "number" ? a.score_percent.toFixed(0) + "%" : "—");
        html.push('<div class="recent-item"><span>' + escapeHtml(a.type) + " · " + escapeHtml((a.topic_id || "").replace(/-/g, " ")) + '</span><span>' + outcome + '</span></div>');
      });
    } else {
      html.push('<div class="empty-state" style="padding:20px;">Nothing yet — start a Practice or Drill session.</div>');
    }
    html.push('</div>');

    // Exam history
    html.push('<div class="card"><div class="card-title">Exam History</div>');
    if (p.exam_history && p.exam_history.length) {
      p.exam_history.forEach(function (e) {
        html.push('<div class="recent-item"><span>' + escapeHtml(new Date(e.date).toLocaleDateString()) + " · " + e.duration_minutes + ' min</span><span>' + e.score_percent.toFixed(1) + '%</span></div>');
      });
    } else {
      html.push('<div class="empty-state" style="padding:20px;">No exams taken yet.</div>');
    }
    html.push('</div>');

    html.push('</div>'); // grid-2

    container.innerHTML = html.join("\n");
  }).catch(function (e) {
    Components.reportError(e, "Could not load dashboard");
    container.innerHTML = '<div class="empty-state"><div class="icon">⚠</div>Could not reach the backend. Is the server running?</div>';
  });
};

function statTile(value, label) {
  return '<div class="stat-tile"><div class="stat-value">' + value + '</div><div class="stat-label">' + escapeHtml(label) + '</div></div>';
}

function masteryRow(t) {
  const pct = Math.round(t.mastery_percent || 0);
  const cls = Components.barFillClass(t.status);
  return '<div class="bar-row">' +
    '<div class="bar-label"><a href="#/learn/' + encodeURIComponent(t.topic_id) + '" style="color:inherit;text-decoration:none;">' + escapeHtml(t.title || t.topic_id) + '</a></div>' +
    '<div class="bar-track" style="flex:1;"><div class="bar-fill ' + cls + '" style="width:' + pct + '%;"></div></div>' +
    '<div class="bar-value">' + pct + '%</div>' +
    '</div>';
}
