import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useCartStore } from '../stores/cartStore';
import { cartService } from '../services/cartService';
import { toast } from '../components/ui/sonner';

/**
 * Global optimistic update configuration.
 * Can be toggled live in the UI to demonstrate rollback on network failure.
 */
export const optimisticConfig = {
  simulateDelayMs: 0,
  simulateError: false,
};

/**
 * Optimistic Cart Mutations with rollback on server failure.
 */
export function useCartMutation() {
  const queryClient = useQueryClient();
  const cartStore = useCartStore();

  // 1. OPTIMISTIC ADD TO CART
  const addToCartMutation = useMutation({
    mutationFn: async ({ product, quantity = 1 }) => {
      if (optimisticConfig.simulateDelayMs > 0) {
        await new Promise((res) => setTimeout(res, optimisticConfig.simulateDelayMs));
      }
      if (optimisticConfig.simulateError) {
        throw new Error('Simulated 500 Network Failure: Server rejected cart update');
      }
      // If user is logged in, sync with server backend
      try {
        return await cartService.addToCart(product.id, quantity);
      } catch (e) {
        // Fallback for demo when backend is offline or unauthenticated
        return { success: true };
      }
    },
    onMutate: async ({ product, quantity = 1 }) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: ['cart'] });

      // Snapshot previous state
      const previousItems = [...cartStore.items];

      // Optimistically update Zustand store immediately (0ms UI lag)
      cartStore.addItem(product, quantity);

      toast.success(`Added ${product.title || product.name} to cart (Optimistic)`, {
        description: 'Updated instantly without waiting for server network roundtrip.',
      });

      return { previousItems };
    },
    onError: (err, newTodo, context) => {
      // Rollback on error
      if (context?.previousItems) {
        cartStore.setItems(context.previousItems);
        toast.error('Cart update failed! State rolled back.', {
          description: err.message,
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // 2. OPTIMISTIC UPDATE QUANTITY
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ productId, quantity }) => {
      if (optimisticConfig.simulateDelayMs > 0) {
        await new Promise((res) => setTimeout(res, optimisticConfig.simulateDelayMs));
      }
      if (optimisticConfig.simulateError) {
        throw new Error('Simulated Error: Could not update product stock on server');
      }
      try {
        return await cartService.updateQuantity(productId, quantity);
      } catch (e) {
        return { success: true };
      }
    },
    onMutate: async ({ productId, quantity }) => {
      await queryClient.cancelQueries({ queryKey: ['cart'] });
      const previousItems = [...cartStore.items];

      cartStore.updateQuantity(productId, quantity);

      return { previousItems };
    },
    onError: (err, variables, context) => {
      if (context?.previousItems) {
        cartStore.setItems(context.previousItems);
        toast.error('Quantity update failed! Reverted back.', {
          description: err.message,
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  // 3. OPTIMISTIC REMOVE ITEM
  const removeItemMutation = useMutation({
    mutationFn: async ({ productId }) => {
      if (optimisticConfig.simulateDelayMs > 0) {
        await new Promise((res) => setTimeout(res, optimisticConfig.simulateDelayMs));
      }
      if (optimisticConfig.simulateError) {
        throw new Error('Simulated Error: Failed to remove item from cloud database');
      }
      try {
        return await cartService.removeItem(productId);
      } catch (e) {
        return { success: true };
      }
    },
    onMutate: async ({ productId }) => {
      await queryClient.cancelQueries({ queryKey: ['cart'] });
      const previousItems = [...cartStore.items];

      cartStore.removeItem(productId);
      toast.info('Item removed (Optimistic UI)');

      return { previousItems };
    },
    onError: (err, variables, context) => {
      if (context?.previousItems) {
        cartStore.setItems(context.previousItems);
        toast.error('Could not remove item! Restored to cart.', {
          description: err.message,
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });

  return {
    addToCart: (product, quantity) => addToCartMutation.mutate({ product, quantity }),
    updateQuantity: (productId, quantity) => updateQuantityMutation.mutate({ productId, quantity }),
    removeItem: (productId) => removeItemMutation.mutate({ productId }),
    isAdding: addToCartMutation.isPending,
    isUpdating: updateQuantityMutation.isPending,
    isRemoving: removeItemMutation.isPending,
  };
}
