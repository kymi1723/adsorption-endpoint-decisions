"""python -m endpoint_release: frozen evaluation is the default."""
import argparse
from .io import ROOT,output,read,write

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command')
    a=sub.add_parser('evaluate');a.add_argument('--scheme',choices=['U0-E','Original_frozen'],default='U0-E');a.add_argument('--out',default='outputs/frozen_U0_E')
    a=sub.add_parser('build');a.add_argument('--out',default='outputs/rebuilt');a.add_argument('--recompute-pso',action='store_true')
    a=sub.add_parser('train');a.add_argument('--out',default='outputs/retrained');a.add_argument('--all-cases',action='store_true');a.add_argument('--recompute-pso',action='store_true')
    a=sub.add_parser('predict');a.add_argument('input');a.add_argument('--out',default='outputs/new_curve');a.add_argument('--configuration',choices=['common_U0_E','original_frozen','laboratory_source_excluded'],default='common_U0_E')
    a=sub.add_parser('laboratory');a.add_argument('--out',default='outputs/laboratory')
    a=sub.add_parser('figures');a.add_argument('--out',default='outputs/figures')
    a=sub.add_parser('verify');a.add_argument('--out',default='outputs/verification')
    a=sub.add_parser('comparators');a.add_argument('--out',default='outputs/fixed_time_comparators')
    args=p.parse_args()
    if args.command is None:args=p.parse_args(['evaluate'])
    out=output(args.out)
    if args.command=='evaluate':
        from .evaluation import evaluate
        evaluate(out,args.scheme)
    elif args.command=='build':
        from .build import build
        build(out,args.recompute_pso)
    elif args.command=='train':
        from .training import train
        train(out,args.all_cases,args.recompute_pso)
    elif args.command=='predict':
        from .inference import predict
        write(out/'prediction.json',predict(read(args.input),configuration=args.configuration))
    elif args.command=='laboratory':
        from .inference import laboratory
        laboratory(out)
    elif args.command=='figures':
        from .figures import figures
        figures(out)
    elif args.command=='verify':
        from .verification import verify
        verify(out)
    elif args.command=='comparators':
        from .comparators import replay_fixed
        replay_fixed(out)
if __name__=='__main__':main()
