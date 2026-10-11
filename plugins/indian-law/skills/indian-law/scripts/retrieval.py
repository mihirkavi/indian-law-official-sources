# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf==6.20.0"]
# ///
"""Public evidence CLI. Feed secret-free JSON on stdin; evidence directory is explicit."""
import argparse
import json
from pathlib import Path
import sys
from documents import EvidenceError, EvidenceStore


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['sources','fetch','read','check-quote'])
    parser.add_argument('--store',type=Path,required=True,help='Authorized local matter evidence directory')
    parser.add_argument('--registry',type=Path,default=Path(__file__).resolve().parents[1]/'references/sources.json')
    args=parser.parse_args()
    try:
        registry=json.loads(args.registry.read_text())
        store=EvidenceStore(args.store,registry)
        data={} if args.operation=='sources' else json.load(sys.stdin)
        if not isinstance(data,dict):
            raise EvidenceError('Object input required')
        if args.operation=='sources':output=store.catalog()
        elif args.operation=='fetch':output=store.fetch(data['source_id'],data['url'])
        elif args.operation=='read':output=store.read(data['document_id'],data.get('query'),data.get('pdf_page'))
        else:output=store.check_quote(data['document_id'],data['quote'],data.get('pdf_page'))
        print(json.dumps(output,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError):
        print(json.dumps({'status':'invalid_input','reason':'Use documented secret-free input and an authorized evidence directory.'}))
        return 2


if __name__=='__main__':raise SystemExit(main())
