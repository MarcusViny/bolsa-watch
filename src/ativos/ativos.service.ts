import { Injectable, NotFoundException } from '@nestjs/common';
import * as fs from 'fs/promises';
import * as path from 'path';

export interface Ativo {
  ticker: string;
  preco: string;
  dy: string;
  pvp: string;
}

@Injectable()
export class AtivosService {
  private cache: Ativo[] = [];

  async carregarCache() {
    const filePath = path.join(__dirname, '..', '..', 'ativos.json');
    const data = await fs.readFile(filePath, 'utf-8');
    this.cache = JSON.parse(data) as Ativo[];
  }

  async buscarTodos(): Promise<Ativo[]> {
    if (!this.cache.length) {
      await this.carregarCache();
    }
    return this.cache;
  }

  async buscarPorTicker(ticker: string): Promise<Ativo> {
    if (!this.cache.length) {
      await this.carregarCache();
    }
    const ativo = this.cache.find(
      (a) => a.ticker.toLowerCase() === ticker.toLowerCase(),
    );
    if (!ativo) {
      throw new NotFoundException(`Ativo ${ticker} não encontrado`);
    }
    return ativo;
  }
}
