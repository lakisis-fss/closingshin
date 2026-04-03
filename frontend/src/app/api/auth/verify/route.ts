import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const { password } = await request.json();

        // 런타임(Runtime)에 최신 환경변수 파일(.env)을 읽어옴
        // NEXT_PUBLIC_ 이 붙지 않은 변수는 빌드 시점에 박제되지 않고, 서버 실행 시점에 동적으로 평가됨
        const correctPassword = process.env.SITE_PASSWORD || process.env.NEXT_PUBLIC_SITE_PASSWORD || "1234";

        if (password === correctPassword) {
            return NextResponse.json({ success: true });
        } else {
            return NextResponse.json({ success: false }, { status: 401 });
        }
    } catch (error) {
        return NextResponse.json({ success: false, error: 'Invalid request' }, { status: 400 });
    }
}
