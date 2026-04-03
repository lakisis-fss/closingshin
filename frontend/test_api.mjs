async function test() {
    const res = await fetch("http://localhost:3000/api/portfolio/history?ticker=272210&startDate=2026-01-21");
    console.log("Status:", res.status);
    const text = await res.text();
    console.log("Body length:", text.length);
    try {
        const json = JSON.parse(text);
        console.log("Parse successful. History length:", json.history?.length);
    } catch (e) {
        console.error("Parse failed. Body content:", text);
    }
}
test();
