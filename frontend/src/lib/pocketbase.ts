import PocketBase from 'pocketbase';

const PB_URL = process.env.PB_URL || "http://127.0.0.1:8090";
const pb = new PocketBase(PB_URL);

// 클라이언트 쪽에서는 보통 인증 없이 공개 데이터를 보거나 
// 필요시 나중에 인증 로직을 추가할 수 있습니다.
// 여기서는 기존 fetchFromPB 등의 인터페이스를 유지하며 내부만 SDK로 교체합니다.

export async function fetchFromPB(collection: string, params: any = {}) {
    const { filter, sort, limit = 50, fields } = params;
    
    try {
        const result = await pb.collection(collection).getList(1, limit, {
            filter: filter || '',
            sort: sort || '',
            fields: fields || '',
            requestKey: null, // 중복 요청 취소 방지 (필요시)
        });
        
        return { items: result.items };
    } catch (e: any) {
        console.error(`[PB Debug] PocketBase Fetch Error (${collection}):`, e.message);
        return { items: [] };
    }
}

/**
 * 컬렉션의 모든 데이터를 가져옵니다 (필터/정렬/필드 선택 가능).
 * 대량의 데이터를 가져와야 할 때 (예: 캘린더 날짜 목록) 사용합니다.
 */
export async function getFullListFromPB(collection: string, params: any = {}) {
    const { filter, sort, fields } = params;
    
    try {
        const result = await pb.collection(collection).getFullList({
            filter: filter || '',
            sort: sort || '',
            fields: fields || '',
            requestKey: null,
        });
        
        return { items: result };
    } catch (e: any) {
        console.error(`[PB Debug] PocketBase FullList Error (${collection}):`, e.message);
        return { items: [] };
    }
}

export async function postToPB(collection: string, data: any) {
    try {
        const record = await pb.collection(collection).create(data);
        return record;
    } catch (e: any) {
        console.error(`[PB Debug] PocketBase Post Error (${collection}):`, e.message);
        throw e;
    }
}

export async function patchToPB(collection: string, id: string, data: any) {
    try {
        const record = await pb.collection(collection).update(id, data);
        return record;
    } catch (e: any) {
        console.error(`[PB Debug] PocketBase Patch Error (${collection}):`, e.message);
        throw e;
    }
}

export async function deleteFromPB(collection: string, id: string) {
    try {
        await pb.collection(collection).delete(id);
        return true;
    } catch (e: any) {
        console.error(`[PB Debug] PocketBase Delete Error (${collection}):`, e.message);
        throw e;
    }
}

// SDK 인스턴스를 직접 내보내어 더 복잡한 작업(실시간 구독 등)에 쓸 수 있게 합니다.
export default pb;
