with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Replace star field init with carousel init
old_stars = "    // ===== 精选大卡星空 ====="
end_stars = "    })();\n})();"

idx_start = c.index(old_stars)
idx_end = c.index(end_stars, idx_start) + len(end_stars)

new_carousel = '''    // ===== 精选轮播 =====
    var SR_SLIDES = [
        {title:'🌙 星空漫游', sub:'今晚，陪TA看星星', bg:'linear-gradient(135deg, #1a1a3e 0%, #2d1b4e 50%, #4a2c5e 100%)', scene:'campus'},
        {title:'☕ 咖啡馆初遇', sub:'一杯拿铁的时间，遇见你', bg:'linear-gradient(135deg, #3e2723 0%, #4e342e 50%, #5d4037 100%)', scene:'dating'},
        {title:'🏖️ 海边篝火', sub:'海浪声里，心跳声更清晰', bg:'linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%)', scene:'beach'},
        {title:'🎪 游园惊梦', sub:'旋转木马上的第一次对视', bg:'linear-gradient(135deg, #4a148c 0%, #6a1b9a 50%, #8e24aa 100%)', scene:'workplace'},
    ];
    var srIdx = 0, srTimer = null;

    function renderCarousel() {
        var el = document.getElementById('srFeatured');
        if (!el) return;
        var slidesHTML = SR_SLIDES.map(function(s,i){
            return '<div class="sr-featured-slide'+(i===srIdx?' active':'')+'" style="background:'+s.bg+';" onclick="window.location.href=\\'scene.html\\'">'+
                '<div class="sr-featured-content"><span class="sr-featured-tag">🌟 本月精选</span>'+
                '<div class="sr-featured-title">'+s.title+'</div>'+
                '<div class="sr-featured-sub">'+s.sub+'</div></div></div>';
        }).join('');
        var dotsHTML = SR_SLIDES.map(function(_,i){
            return '<span class="sr-dot'+(i===srIdx?' active':'')+'" onclick="srGo('+i+')"></span>';
        }).join('');
        el.innerHTML = slidesHTML +
            '<button class="sr-arrow left" onclick="srPrev()">◀</button>'+
            '<button class="sr-arrow right" onclick="srNext()">▶</button>'+
            '<div class="sr-dots" id="srDots">'+dotsHTML+'</div>';
    }

    function srGo(idx) {
        srIdx = idx;
        document.querySelectorAll('.sr-featured-slide').forEach(function(s,i){ s.classList.toggle('active', i===srIdx); });
        document.querySelectorAll('.sr-dot').forEach(function(d,i){ d.classList.toggle('active', i===srIdx); });
        resetSrTimer();
    }
    window.srPrev = function() { srGo((srIdx - 1 + SR_SLIDES.length) % SR_SLIDES.length); };
    window.srNext = function() { srGo((srIdx + 1) % SR_SLIDES.length); };

    function resetSrTimer() {
        clearInterval(srTimer);
        srTimer = setInterval(function(){ srGo((srIdx + 1) % SR_SLIDES.length); }, 4500);
    }
    renderCarousel();
    resetSrTimer();'''

c = c[:idx_start] + new_carousel + '\n' + c[idx_end:]

# 2. Update renderAll to use card stack
old_render_all = "    function renderAll() {"
end_render_all = "    }\n\n    // ===== 交互 ====="

idx_start = c.index(old_render_all)
idx_end = c.index(end_render_all, idx_start)

new_render_all = '''    function renderAll() {
        var p = currentIdx < shuffled.length ? shuffled[currentIdx] : null;
        if (!p) { currentIdx = 0; shuffled = shuffle(filtered.slice()); p = shuffled[0]; }
        window._currentMatch = p;
        var next1 = (currentIdx+1 < shuffled.length) ? shuffled[currentIdx+1] : shuffled[0];
        var next2 = (currentIdx+2 < shuffled.length) ? shuffled[currentIdx+2] : (shuffled.length>1?shuffled[0]:null);
        var stackHTML = '<div class="card-stack">' +
            renderMatchCardContent(p, true) +
            renderMatchCardContent(next1, false) +
            (next2 ? renderMatchCardContent(next2, false) : '') +
            '</div>';
        container.innerHTML =
            renderSelfCard() +
            '<div class="dual-heart">💗</div>' +
            stackHTML;
    }

    function renderMatchCardContent(person, isTop) {
        if (!person) return '';
        var tagsHTML = (person.tags||[]).slice(0,3).map(function(t,i){
            return '<span class="sc-tag '+TAG_COLORS[(i+2)%TAG_COLORS.length]+'">'+t+'</span>';
        }).join('');
        return '<div class="side-card match-card card-stack-layer">' +
            '<div class="sc-label">匹配对象</div>' +
            '<div class="sc-avatar" style="background:linear-gradient(135deg,#e8eaf6,#c5cae9);"><span>'+(person.gender==='male'?'🧑‍💻':'👩‍🎨')+'</span></div>' +
            '<div class="sc-name-row">'+person.name+' · '+person.age+'岁 · '+(person.city||'')+'</div>' +
            '<div class="sc-tags">'+tagsHTML+'</div>' +
            '<div class="sc-declaration">'+person.bio+'</div>' +
            (isTop ? '<div class="sc-actions">' +
            '<button class="sc-act-btn nope" onclick="signalNope()" title="不喜欢">✕</button>' +
            '<button class="sc-act-btn like" onclick="signalLike()" title="喜欢">♥</button>' +
            '</div>' : '') +
            '</div>';
    }
'''

c = c[:idx_start] + new_render_all + '\n' + c[idx_end:]

# 3. Update signalNope
old_nope_anim = "var card = document.getElementById('matchSideCard');"
if old_nope_anim in c:
    idx = c.index(old_nope_anim)
    # Find the end of the if/else block
    end_nope = c.index("setTimeout(function(){ currentIdx++; renderAll(); }, 350);", idx)
    end_nope = c.index("}", end_nope) + 1
    c = c[:idx] + "var stack = document.querySelector('.card-stack');\n        if (stack) {\n            var topCard = stack.querySelector('.card-stack-layer:first-child');\n            if (topCard) topCard.classList.add('swiping-left');\n        }" + c[end_nope:]

# 4. Remove old renderMatchCard
old_rmc = "    function renderMatchCard(person) {"
if old_rmc in c:
    start = c.index(old_rmc)
    # Find the closing brace
    brace = 0
    end = start
    for i in range(start, len(c)):
        if c[i] == '{': brace += 1
        elif c[i] == '}':
            brace -= 1
            if brace == 0:
                end = i + 1
                break
    c = c[:start-4] + c[end:]

# 5. Remove old match-card-wrap CSS reference if any
c = c.replace('.match-card.swiping-left', '.card-stack-layer.swiping-left')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('All done')
